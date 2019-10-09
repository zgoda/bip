from typing import List, Optional

from ..models import Category
from . import Filter, Sort, create_object, get_query


def get(pk):
    return Category.query.get(pk)


def create(save=True, **kwargs):
    return create_object(Category, save, **kwargs)


def query(sort: Optional[List[Sort]] = None, filters: Optional[List[Filter]] = None):
    return get_query(Category, sort, filters)
