#!/usr/bin/env python
# coding: utf8

import argparse
import hashlib
import json
import logging
import os
import shutil
import sys
import tarfile
from pathlib import Path
from typing import List

__version__ = '0.1.3'

prog_name = os.path.basename(sys.argv[0])

epilog = """
Expand Rust crates into vendor directory.

Example: Expand a single .crate file::
  $ mkdir vendor
  $ {prog_name} something-1.2.3.crate vendor

Example: Expand a directory of .crate files::
  $ mkdir vendor
  $ mkdir vendor.crates
  $ cp *.crate vendor.crates
  $ {prog_name}  vendor.crates vendor
""".format(
    prog_name=prog_name
)

logging.getLogger().addHandler(logging.StreamHandler(sys.stdout))

logger = logging.getLogger(prog_name)
info = logger.info
debug = logger.debug


def die(message: str) -> None:
    logger.error(message)
    sys.exit(1)


def make_checksum(path: Path) -> str:
    with open(str(path), 'rb') as f:
        hash = hashlib.sha256(f.read()).hexdigest()
    return hash


def tar_extract_files(tar_path: Path, dest_root: Path) -> List[Path]:
    """Extract gzipped tar bilf tar_path into destination directory dest_root.

    Return Paths of extracted files.
    """
    file_paths = []
    with tarfile.open(str(tar_path), 'r:gz') as tar_f:
        for tar_info in tar_f:
            if tar_info.isfile():
                tar_f.extract(tar_info, path=str(dest_root))
                file_paths.append(dest_root / tar_info.name)
    return file_paths


def expand_crate(crate_path: Path, vendor_path: Path, force: bool) -> None:
    dest_path = vendor_path / crate_path.stem
    if dest_path.exists():
        if not force:
            debug('skipping existing crate {}'.format(crate_path.stem))
            return
        info('overwriting existing crate {}'.format(crate_path.stem))
        shutil.rmtree(str(dest_path))
    else:
        info('expanding crate {}'.format(crate_path.stem))

    file_paths = tar_extract_files(crate_path, vendor_path)

    files_meta_data = {
        str(p.relative_to(dest_path)): make_checksum(p) for p in file_paths
    }

    meta_data = {
        'package': make_checksum(crate_path),
        'files': files_meta_data,
    }

    meta_path = dest_path / '.cargo-checksum.json'
    with open(str(meta_path), 'w') as f:
        meta_json = json.dumps(meta_data, sort_keys=True, indent=2) + '\n'
        debug('meta_data for {}'.format(meta_path))
        debug(meta_json)
        f.write(meta_json)


def main() -> None:
    parser = argparse.ArgumentParser(
        epilog=epilog, formatter_class=argparse.RawDescriptionHelpFormatter
    )

    parser.add_argument('--version', action='version', version=__version__)

    parser.add_argument(
        '-v',
        '--verbose',
        action='store_const',
        dest='verbose',
        const=logging.DEBUG,
        help='verbose output for debugging',
    )

    parser.add_argument(
        '-q',
        '--quiet',
        action='store_const',
        dest='verbose',
        const=logging.WARNING,
        help='suppress informational output',
    )

    parser.add_argument(
        'source',
        action='store',
        metavar='SOURCE',
        help='.crate file or directory of .crates.',
    )

    parser.add_argument(
        'vendor',
        action='store',
        metavar='VENDOR_DIR',
        help='destination directory for vendoring',
    )

    parser.add_argument(
        '--force',
        action='store_true',
        default=False,
        help='force regeneration of already-existing vendored crates',
    )

    args = parser.parse_args()
    if args.verbose is None:
        logging.getLogger().setLevel(logging.INFO)
    else:
        logging.getLogger().setLevel(args.verbose)

    source_path = Path(args.source)
    vendor_path = Path(args.vendor)
    if not vendor_path.is_dir():
        die('VENDOR_DIR {} must be existing directory'.format(vendor_path))
    if source_path.is_file():
        expand_crate(source_path, vendor_path, force=args.force)
    elif source_path.is_dir():
        for path in source_path.glob('*.crate'):
            expand_crate(path, vendor_path, force=args.force)

    else:
        die(
            'SOURCE {} must be a single crate or a directory of crates'.format(
                source_path
            )
        )


if __name__ == '__main__':
    main()
