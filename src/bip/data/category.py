from typing import List, Optional

from flask_sqlalchemy import BaseQuery

from ..models import Category
from . import Filter, Sort, create_object, get_object, get_query


def get(pk: int) -> Optional[Category]:
    return get_object(Category, pk)


def create(save: bool = True, **kwargs) -> Category:
    return create_object(Category, save, **kwargs)


def query(
            sort: Optional[List[Sort]] = None, filters: Optional[List[Filter]] = None
        ) -> BaseQuery:
    return get_query(Category, sort, filters)
