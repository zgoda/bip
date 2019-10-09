from ..models import Directory
from . import create_object


def create(save: bool = True, **kwargs) -> Directory:
    return create_object(Directory, save, **kwargs)
