from flask import Flask

from ..config import ALLOWED_EXTENSIONS


class BIPApplication(Flask):

    @property
    def jinja_options(self):
        options = dict(super().jinja_options)
        options.update({
            'trim_blocks': True,
            'lstrip_blocks': True,
        })
        return options


def file_allowed(filename):
    """Determine if file is allowed to be uploaded. This is based only on file
    extension.

    :param filename: name of file
    :type filename: str
    :return: decision result
    :rtype: bool
    """
    return '.' in filename and filename.rsplit('.', 1)[-1].lower() in ALLOWED_EXTENSIONS
