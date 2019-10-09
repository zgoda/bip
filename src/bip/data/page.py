from ..models import Page
from . import create_object


def create(save: bool = True, **kwargs) -> Page:
    return create_object(Page, save, **kwargs)
