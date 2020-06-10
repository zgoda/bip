import hashlib
import os
import shutil
from collections import namedtuple

import magic

FileData = namedtuple('FileData', ['filename', 'file_type', 'file_size'])


def process_incoming_file(path: str, target_dir: str) -> FileData:
    """Processing of incoming page attachment file.

    :param path: path to file in local filesystem
    :type path: str
    :param target_dir: destination where the file will be stored
    :type target_dir: str
    :return: file object related data for attachment
    :rtype: FileData
    """
    os.makedirs(target_dir, exist_ok=True)
    file_name_hash = calc_sha256(path)
    _, name = os.path.split(path)
    _, ext = os.path.splitext(name)
    new_file_name = f'{file_name_hash}{ext}'
    file_type = magic.from_file(path, mime=True)
    file_size = os.stat(path).st_size
    target = os.path.join(target_dir, new_file_name)
    shutil.copy2(path, target)
    return FileData(filename=new_file_name, file_type=file_type, file_size=file_size)


def calc_sha256(filename: str) -> str:
    """Calculate SHA256 checksum without reading whole file into memory.

    :param filename: path to file
    :type filename: str
    :return: SHA256 checksum of file content
    :rtype: str
    """
    h = hashlib.sha256()
    b = bytearray(128 * 1024)
    mv = memoryview(b)
    with open(filename, mode='rb', buffering=0) as fp:
        for n in iter(lambda: fp.readinto(mv), 0):
            h.update(mv[:n])
    return h.hexdigest()
