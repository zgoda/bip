from ._version import get_version
from .app import make_app  # noqa: F401

__version__ = get_version()
del get_version
