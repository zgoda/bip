from collections import namedtuple
from typing import Any, List, Optional, Type, TypeVar

from flask_sqlalchemy import BaseQuery, Model
from sqlalchemy_filters import apply_filters, apply_sort

from ..ext import db
from ..utils.http import or_404

Filter = namedtuple('Filter', 'field,op,value,model', defaults=(None,))

Sort = namedtuple(
    'Sort', 'field,direction,model,nullsfirst,nullslast',
    defaults=('asc', None, None, None),
)

ModelVar = TypeVar('ModelVar', bound=Model)


def create_object(klass: Type[ModelVar], save=True, **kwargs: Any) -> ModelVar:
    obj = klass(**kwargs)
    if save:
        db.session.add(obj)
        db.session.commit()
    return obj


def get_object(klass: Type[ModelVar], pk: Any, abort_on_none: bool = False) -> ModelVar:
    obj = klass.query.get(pk)
    if abort_on_none:
        return or_404(obj)
    return obj


def get_query(
            klass: Type[ModelVar], sort: Optional[List[Sort]] = None,
            filters: Optional[List[Filter]] = None,
        ) -> BaseQuery:
    q = klass.query
    if filters:
        q = apply_filters(q, [f._asdict() for f in filters])
    if sort:
        q = apply_sort(q, [s._asdict() for s in sort])
    return q
