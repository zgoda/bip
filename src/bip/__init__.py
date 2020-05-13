from .app import make_app  # noqa: F401
from .__version__ import get_version

__version__ = get_version()

del get_version
