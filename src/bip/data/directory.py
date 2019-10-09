from ..models import Directory
from . import create_object


def create(save=True, **kwargs):
    return create_object(Directory, save, **kwargs)
