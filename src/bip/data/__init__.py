from __future__ import annotations

from collections import namedtuple
from typing import Any, List, Optional, Type

from flask_sqlalchemy import BaseQuery, Model
from sqlalchemy_filters import apply_filters, apply_sort

from ..ext import db
from ..models import Category, Directory
from ..utils.http import or_404

Filter = namedtuple('Filter', 'field,op,value,model', defaults=(None,))

Sort = namedtuple(
    'Sort', 'field,direction,model,nullsfirst,nullslast',
    defaults=('asc', None, None, None),
)


class AccessObject:

    klass_ = None

    @classmethod
    def for_class(cls, klass_):
        obj = cls()
        obj.klass_ = klass_
        return obj

    def create(self, save: bool = True, **kwargs) -> Model:
        obj = self.klass_(**kwargs)
        if save:
            db.session.add(obj)
            db.session.commit()
        return obj

    def get(self, pk: Any, abort_on_none: bool = False) -> Model:
        obj = self.klass_.query.get(pk)
        if abort_on_none:
            return or_404(obj)
        return obj

    def query(
                self, sort: Optional[List[Sort]] = None,
                filters: Optional[List[Filter]] = None,
            ) -> BaseQuery:
        q = self.klass_.query
        if filters:
            q = apply_filters(q, [f._asdict() for f in filters])
        if sort:
            q = apply_sort(q, [s._asdict() for s in sort])
        return q


directory = AccessObject.for_class(Directory)
category = AccessObject.for_class(Category)


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
