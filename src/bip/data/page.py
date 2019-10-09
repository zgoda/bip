from ..models import Page
from . import create_object


def create(save=True, **kwargs):
    return create_object(Page, save, **kwargs)
