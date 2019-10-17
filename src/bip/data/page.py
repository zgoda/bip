from typing import List, Optional

from flask_sqlalchemy import BaseQuery

from ..models import Page
from . import Filter, Sort, create_object, get_query


def create(save: bool = True, **kwargs) -> Page:
    return create_object(Page, save, **kwargs)


def query(
            sort: Optional[List[Sort]] = None, filters: Optional[List[Filter]] = None
        ) -> BaseQuery:
    return get_query(Page, sort, filters)


def category_names(page: Page) -> List[str]:
    return [c.title for c in page.categories]


def directory_names(page: Page) -> List[str]:
    return [d.title for d in page.directories]
