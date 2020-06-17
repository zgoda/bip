from typing import Optional, Union
from math import ceil

from flask import current_app, request, url_for
from peewee import Query


class Pagination:
    """Copied almost verbatim from Flask-SQLAlchemy. Minor changes made to
    work with Peewee query object. Removed unused code.

    Copyright 2010 Pallets
    """

    def __init__(self, query, page, per_page, total, items):
        self.query = query
        self.page = page
        self.per_page = per_page
        self.total = total
        self.items = items

    @property
    def pages(self):
        """The total number of pages"""
        if self.per_page == 0 or self.total is None:
            pages = 0
        else:
            pages = int(ceil(self.total / float(self.per_page)))
        return pages

    @property
    def has_prev(self):
        """True if a previous page exists"""
        return self.page > 1

    @property
    def has_next(self):
        """True if a next page exists."""
        return self.page < self.pages

    def iter_pages(self, left_edge=2, left_current=2, right_current=5, right_edge=2):
        last = 0
        for num in range(1, self.pages + 1):
            if num <= left_edge or \
                    (
                        num > self.page - left_current - 1 and
                        num < self.page + right_current
                    ) or num > self.pages - right_edge:
                if last + 1 != num:
                    yield None
                yield num
                last = num


def url_for_other_page(page: Union[int, str]) -> str:
    """Generate (internal) URL to another page of the same document. This
    works only within the context of particular request.

    :param page: desired page
    :type page: Union[int, str]
    :return: URL to another page of current document
    :rtype: str
    """
    args = request.view_args.copy()
    args['p'] = page
    return url_for(request.endpoint, **args)


def get_page(arg_name: str = 'p') -> int:
    """Get page number for current request. Page number is searched in request
    args.

    :param arg_name: name of URL argument, defaults to 'p'
    :type arg_name: str, optional
    :return: page number or 1 if not found
    :rtype: int
    """
    try:
        return int(request.args.get(arg_name, '1'))
    except ValueError:
        return 1


def paginate(
            query: Query, page: Optional[int] = None, size: Optional[int] = None
        ) -> Pagination:
    """Create pagination object using sane defaults.

    :param query: query to paginate results
    :type query: peewee.Query
    :param page: page number, will be fetched from request if omitted, defaults to
                 None
    :type page: Optional[int], optional
    :param size: page size, defaults to None
    :type size: Optional[int], optional
    :return: pagination object for query
    :rtype: Pagination
    """
    if page is None:
        page = get_page()
    if size is None:
        size = current_app.config.get('LIST_SIZE', 20)
    q = query.paginate(page, size)
    return Pagination(query, page, size, query.count(), q)
