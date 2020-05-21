import hashlib


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
