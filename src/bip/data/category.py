from typing import List, Optional

from sqlalchemy_filters import apply_filters, apply_sort

from ..models import Category
from . import Filter, Sort, create_object


def get(pk):
    return Category.query.get(pk)


def create(save=True, **kwargs):
    return create_object(Category, save, **kwargs)


def query(sort: Optional[List[Sort]] = None, filters: Optional[List[Filter]] = None):
    q = Category.query
    if filters:
        q = apply_filters(q, [f._asdict() for f in filters])
    if sort:
        q = apply_sort(q, [s._asdict() for s in sort])
    return q
