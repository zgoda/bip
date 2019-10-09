from collections import namedtuple
from typing import List, Optional

from sqlalchemy_filters import apply_filters, apply_sort

from ..ext import db

Filter = namedtuple('Filter', 'field,op,value,model', defaults=(None, None))

Sort = namedtuple(
    'Sort', 'field,direction,model,nullsfirst,nullslast',
    defaults=('asc', None, None, None),
)


def create_object(klass, save=True, **kwargs):
    obj = klass(**kwargs)
    if save:
        db.session.add(obj)
        db.session.commit()
    return obj


def get_query(
            klass, sort: Optional[List[Sort]] = None,
            filters: Optional[List[Filter]] = None,
        ):
    q = klass.query
    if filters:
        q = apply_filters(q, [f._asdict() for f in filters])
    if sort:
        q = apply_sort(q, [s._asdict() for s in sort])
    return q
