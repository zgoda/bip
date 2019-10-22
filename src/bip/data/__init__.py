from __future__ import annotations

from collections import namedtuple
from typing import Any, List, Optional, Type

from flask_sqlalchemy import BaseQuery, Model
from sqlalchemy_filters import apply_filters, apply_sort

from ..ext import db
from ..utils.http import or_404

Filter = namedtuple('Filter', 'field,op,value,model', defaults=(None,))

Sort = namedtuple(
    'Sort', 'field,direction,model,nullsfirst,nullslast',
    defaults=('asc', None, None, None),
)


def create_object(klass: Type[Model], save=True, **kwargs: Any) -> Model:
    obj = klass(**kwargs)
    if save:
        db.session.add(obj)
        db.session.commit()
    return obj


def get_object(klass: Type[Model], pk: Any, abort_on_none: bool = False) -> Model:
    obj = klass.query.get(pk)
    if abort_on_none:
        return or_404(obj)
    return obj


def get_query(
            klass: Type[Model], sort: Optional[List[Sort]] = None,
            filters: Optional[List[Filter]] = None,
        ) -> BaseQuery:
    q = klass.query
    if filters:
        q = apply_filters(q, [f._asdict() for f in filters])
    if sort:
        q = apply_sort(q, [s._asdict() for s in sort])
    return q
