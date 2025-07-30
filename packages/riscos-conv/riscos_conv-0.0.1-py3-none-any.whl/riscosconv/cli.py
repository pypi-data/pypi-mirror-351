import argparse
import os
import re
import struct
import sys
import time
from collections import namedtuple
from datetime import datetime
from enum import Enum
from io import BytesIO
from pathlib import Path
from typing import IO, Optional
from zipfile import ZipFile, is_zipfile

from .adfslib import ADFS_exception, ADFSdirectory, ADFSdisc, ADFSfile
from .filetypes import RISC_OS_FILETYPES
from .nspark import NSparkArchive
from .riscos_zip import RiscOsZip, convert_disc_to_zip, get_riscos_zipinfo
from .ro_file_meta import DiscImageBase, FileMeta, RiscOsFileMeta
from .sprites import SpriteArea, list_sprites

DISC_IM_EXTS = ('.adf','.adl')


class KnownFileType(Enum):
    RISC_OS_ZIP = 1
    ZIPPED_DISC_IMAGE = 2
    ZIPPED_MULTI_DISC_IMAGE = 3
    DISC_IMAGE = 4
    SPARK_ARCHIVE = 5
    ARCFS_ARCHIVE = 6
    RISC_OS_SPRITES = 7
    UNKNOWN = 8

def has_disc_image_ext(filename: str) -> bool:
    return any(filename.lower().endswith(ext) for ext in DISC_IM_EXTS)


class RiscOsAdfsDisc(DiscImageBase):
    def __init__(self, fd):
        self.disc = ADFSdisc(fd)

    def __repr__(self):
        return f'ADFS Disc - {self.disc.disc_name}'
    
    @property
    def disc_name(self):
        return self.disc.disc_name
    
    def list(self, files=None, path=''):
        if files is None:
            files = self.disc.files
        for f in files:
            if isinstance(f, ADFSfile):
                ro_meta = RiscOsFileMeta(f.load_address, f.execution_address)
                ds = ro_meta.datestamp
                if not ds:
                    ds = datetime.now()
                # TODO: properly support/convert RISC OS paths via new pathlib type
                filename = f.name.replace('/', '.')
                full_path = (path + '/' + filename).removeprefix('/')
                yield full_path, FileMeta(ro_meta, ds, f.length)
            elif isinstance(f, ADFSdirectory):
                yield from self.list(f.files, path + '/' + f.name)
            
    def get_file_meta(self, path):
        f = self.disc.get_path(path)
        ro_meta = RiscOsFileMeta(f.load_address, f.execution_address)
        ds = ro_meta.datestamp
        if not ds:
            ds = datetime.now()
        return FileMeta(ro_meta, ds, f.length)

    def open(self, path) -> IO[bytes]:
        f = self.disc.get_path(path)
        if not f:
            return None
        return BytesIO(f.data)
    


def load_ro_filetypes():
    filetype_map = {}
    for l in open('filetypes.txt', 'r'):
        bits = re.split(r'\t', l.strip(), maxsplit=2)
        if len(bits) == 2:
            bits.append('')
        if len(bits) != 3:
            print(len(bits), l.strip())
        filetype, name, desc = bits
        filetype = int(filetype, 16)
        filetype_map[filetype] = name, desc
    return filetype_map

#FILETYPE_MAP = load_ro_filetypes()

def ro_path_to_path(ro_path) -> Path:
    p = Path()
    for s in ro_path.split('.'):
        p /= s
    return p

def adfs_extract_ro_path(disc: ADFSdisc, path: Path, filetype=None):
    for file in disc.files:
        print(file)
        

def save_filetypes():
    with open('filetypes.py', 'w') as f:
        f.write('RISC_OS_FILETYPES = {\n')
        for filetype, (name, desc) in FILETYPE_MAP.items():
            f.write('  0x{:03x}: ({}, {}),\n'.format(filetype, repr(name), repr(desc)))
        f.write('}\n')

#save_filetypes()

def list_disc(disc: DiscImageBase):
    for file_name, file_meta in disc.list():
        ro_meta = file_meta.ro_meta
        ds = file_meta.timestamp
        if ro_meta:
            if ro_meta.filetype:
                name, desc = RISC_OS_FILETYPES.get(ro_meta.filetype, (None, None))
                if name:
                    extra = f'{name} {ro_meta.filetype:03x}'
                else:
                    extra = f'{ro_meta.filetype:03x}'
            else:
                extra = f'{ro_meta.load_addr:08x}-{ro_meta.exec_addr:08x}'
        else:
            extra = ''
        date_formatted = ds.strftime('%Y-%m-%d %H:%M:%S')
        print(f'{extra: >17} {file_meta.file_size: >7} {date_formatted} {file_name}')

def many_files_in_root(disc: DiscImageBase):
    files_in_root = set()
    for file_name, meta in disc.list():
        first = file_name.split('/', 1).pop(0)
        files_in_root.add(first)
    return len(files_in_root) > 1

def extract_riscos_disc(disc: DiscImageBase, path='.'):
    if many_files_in_root(disc):
        name, _ = os.path.splitext(os.path.basename(disc.disc_name))
        path += '/' + name
    print(f'Extracting to {path}:')
    for filename, meta in disc.list():
        ro_meta = meta.ro_meta
        extract_path = os.path.join(path, filename + ro_meta.hostfs_file_ext())
        print(' ', extract_path)
        extract_dir = os.path.dirname(extract_path)
        os.makedirs(extract_dir, exist_ok=True)
        with disc.open(filename) as f:
            with open(extract_path, 'wb') as ff:
                ff.write(f.read())
        ds = meta.timestamp
        if ds:
            ts = time.mktime(ds.timetuple())
            ts_ns = int(ts * 1_000_000_000) + ds.microsecond * 1000
            os.utime(extract_path, ns=(ts_ns,ts_ns))

def extract_riscos_sprites(sprite_area: SpriteArea, path='.'):
    print(f'Extracting to {path}')
    for spr in sprite_area.sprites():
        out_name = f'{path}/{spr.name}.png'
        print(f'  {out_name}')
        spr.get_pil_image().save(out_name)

def add_file_to_zip(zipfile: ZipFile, filepath: Path, base_path: Path):
    zipinfo = get_riscos_zipinfo(filepath, base_path)
    ro_meta = zipinfo.getRiscOsMeta()
    print(zipinfo.filename, ro_meta)
    with open(filepath, 'rb') as f:
        zipfile.writestr(zipinfo, f.read(), compresslevel=9)

def add_dir_tree_to_zip(zipfile: ZipFile, dirpath: Path, basepath: Path):
    for root, dirs, files in os.walk(dirpath):
        for filename in files:
            filepath = Path(root) / filename
            add_file_to_zip(zipfile, filepath, basepath)
          
def create_riscos_zipfile(zipfile: ZipFile, paths: list[str]|str):
    if type(paths) is str:
        paths = [paths]

    for path in paths:
        path = Path(path)
        if path.is_file():
            add_file_to_zip(zipfile, path, os.path.dirname(path))
        elif path.is_dir():
            dirname = path.name
            basepath = path
            if dirname.startswith('!'):
                basepath = path.parent
            add_dir_tree_to_zip(zipfile, path, basepath)
  
def identify_zipfile(zipfile: ZipFile):
    num_ro_meta = 0
    num_discim_exts = 0
    for info in zipfile.infolist():
        ro_meta = info.getRiscOsMeta()
        if ro_meta:
            num_ro_meta +=1
        if has_disc_image_ext(info.filename):
            num_discim_exts += 1

    if num_discim_exts == 1:
        item_fd = zipfile.open(info, 'r')
        result = identify_discimage(info.filename, item_fd)
        if result == KnownFileType.DISC_IMAGE:
            return KnownFileType.ZIPPED_DISC_IMAGE
        return KnownFileType.UNKNOWN
    if num_discim_exts > 1:
        raise Exception('not support multi disc zips')
    if num_ro_meta >= 1:
        return KnownFileType.RISC_OS_ZIP
    

def identify_discimage(filename: str, fd):
    try:
        ADFSdisc(fd)
        return KnownFileType.DISC_IMAGE
    except ADFS_exception:
        return KnownFileType.UNKNOWN

def identify_file(filename: str, fd) -> KnownFileType:

    if filename.endswith(',ff9'):
        return KnownFileType.RISC_OS_SPRITES
    
    if is_zipfile(fd):
        zipfile = ZipFile(fd)
        return identify_zipfile(zipfile)
    
    fd.seek(0, os.SEEK_SET)
    data = fd.read(12)
    fd.seek(0, os.SEEK_SET)

    # From spark.h in NSpark
    if data[0] == 0x1a and (data[1] & 0xf0 == 0x80 or data[1] == 0xff):
        return KnownFileType.SPARK_ARCHIVE
  
    if data[0:8] == b'Archive\x00':
        return KnownFileType.ARCFS_ARCHIVE
  
    num_sprites, first_offset, next_free = struct.unpack('<III', data)
    size = fd.seek(0, os.SEEK_END)
    fd.seek(0, os.SEEK_SET)
    if first_offset == 16 and next_free == size + 4:
        return KnownFileType.RISC_OS_SPRITES
    
    return identify_discimage(filename, fd)

def load_disc(main_file: str) -> Optional[DiscImageBase]:
    with open(main_file, 'rb') as fd:
        file_type = identify_file(main_file, fd)
    if file_type == KnownFileType.UNKNOWN:
        return None
    fd = open(main_file, 'rb')
    if file_type == KnownFileType.ZIPPED_DISC_IMAGE:
        fd = extract_single_disc_image_from_zip(fd)
        file_type = KnownFileType.DISC_IMAGE
    riscos_disc = HANDLER_FNS[file_type](fd)
    return riscos_disc

def extract_single_disc_image_from_zip(fd):
    zipfile = ZipFile(fd, 'r')
    for info in zipfile.infolist():
        if has_disc_image_ext(info.filename):
            return zipfile.open(info, 'r')
    raise Exception("Did not find single disc image in ZIP file")


def extract_disc_image(fd, path='.'):
    adfs = ADFSdisc(fd)

    if len(adfs.files) > 1:
        path = path + '/' + adfs.disc_name
        os.makedirs(path, exist_ok=True)
    adfs.extract_files(path, with_time_stamps=True, filetypes=True)


HandlerFns = namedtuple('HandlerFns', ['list', 'extract', 'create'], defaults=(None,))

HANDLER_FNS = {
    KnownFileType.DISC_IMAGE: RiscOsAdfsDisc,
    KnownFileType.RISC_OS_ZIP: RiscOsZip,
    KnownFileType.ARCFS_ARCHIVE: NSparkArchive,
    KnownFileType.SPARK_ARCHIVE: NSparkArchive,
    KnownFileType.RISC_OS_SPRITES: SpriteArea
}

LIST_FNS = {
    KnownFileType.DISC_IMAGE: list_disc,
    KnownFileType.RISC_OS_ZIP: list_disc,
    KnownFileType.ARCFS_ARCHIVE: list_disc,
    KnownFileType.SPARK_ARCHIVE: list_disc,
    KnownFileType.RISC_OS_SPRITES: list_sprites
}

EXTRACT_FNS = {
    KnownFileType.DISC_IMAGE: extract_riscos_disc,
    KnownFileType.RISC_OS_ZIP: extract_riscos_disc,
    KnownFileType.ARCFS_ARCHIVE: extract_riscos_disc,
    KnownFileType.SPARK_ARCHIVE: extract_riscos_disc,
    KnownFileType.RISC_OS_SPRITES: extract_riscos_sprites
}

def cli():
    parser = argparse.ArgumentParser(prog='riscos-conv', description="Extract and create RISC OS ZIP files")
    parser.add_argument('-d', '--dir', default='.', help='Output directory')
    parser.add_argument('-a', '--append', action='store_true', help='Append files to existing archive')
    parser.add_argument('action', choices=['x','l','c','d2z'], nargs='?', default='l', help='e[x]tract, [l]ist, [c]reate archive or convert disc to ZIP archive [d2z]')
    parser.add_argument('file', help='ZIP or (zipped) disc file to create or list/extract')  
    parser.add_argument('files', nargs='*', help='Files to extract / add')
    args = parser.parse_args()

    main_file = args.file

    if args.action in ('l', 'x', 'd2z'):
        if not os.path.isfile(main_file):
            sys.stderr.write(f'file not found: {main_file}\n')
            sys.exit(-1)
        fd = open(main_file, 'rb')
        file_type = identify_file(main_file, fd)
        if file_type == KnownFileType.UNKNOWN:
            sys.stderr.write(f'{main_file}: unknown file type\n')
            sys.exit(-1)
        print(f'file type {file_type.name}')
        if file_type == KnownFileType.ZIPPED_DISC_IMAGE:
            fd = extract_single_disc_image_from_zip(fd)
            file_type = KnownFileType.DISC_IMAGE

    elif args.action == 'c':
        if not main_file.lower().endswith('.zip'):
            sys.stderr.write('Only support creating zip files\n')
            sys.exit(-1)
    
    if args.action == 'd2z':
        if file_type not in (KnownFileType.DISC_IMAGE, KnownFileType.ARCFS_ARCHIVE, KnownFileType.SPARK_ARCHIVE):
            sys.stderr.write('Must provide disc image to convert to archive\n')
            sys.exit(-1)
        if len(args.files) == 0:
            sys.stderr.write('Must provide an output ZIP filename\n')
            sys.exit(-1)
        output_zip_path = args.files[0]
        extract_paths = args.files[1:]

   
    match args.action:
        case 'l':
            riscos_disc = HANDLER_FNS[file_type](fd)
            print(riscos_disc)
            LIST_FNS[file_type](riscos_disc)
        case 'x':
            riscos_disc = HANDLER_FNS[file_type](fd)
            print(riscos_disc)
            assert os.path.isdir(args.dir)
            EXTRACT_FNS[file_type](riscos_disc, args.dir)
        case 'c':
            mode = 'w'
            if args.append:
                mode = 'a'
            zip = ZipFile(main_file, mode)
            create_riscos_zipfile(zip, args.files)
        case 'd2z':
            riscos_disc = HANDLER_FNS[file_type](fd)
            print(riscos_disc)
            convert_disc_to_zip(riscos_disc, output_zip_path, extract_paths)


if __name__ == '__main__':
    cli()
