from __future__ import annotations

from collections import namedtuple
from typing import Any, List, Optional, Type, Union

from flask_sqlalchemy import BaseQuery, Model
from sqlalchemy_filters import apply_filters, apply_sort

from .ext import db
from .models import Category, ChangeRecord, ChangeType, Directory, Page, User
from .utils.http import or_404

Filter = namedtuple('Filter', 'field,op,value,model', defaults=(None, None))

Sort = namedtuple(
    'Sort', 'field,direction,model,nullsfirst,nullslast',
    defaults=('asc', None, None, None),
)


class AccessObject:

    klass_ = None

    @classmethod
    def for_class(cls, klass_: Type[Model]) -> AccessObject:
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


class UserAccessObject(AccessObject):

    @classmethod
    def make(cls) -> UserAccessObject:
        return cls.for_class(User)

    def create(self, save: bool = True, **kwargs) -> User:
        password = kwargs.pop('password')
        user = super().create(save=False, **kwargs)
        user.set_password(password)
        if save:
            db.session.add(user)
            db.session.commit()
        return user

    def by_name(self, name: str, **params) -> Optional[User]:
        return self.klass_.query.filter_by(name=name, **params).first()


class ChangeAccessObject(AccessObject):

    @classmethod
    def make(cls) -> ChangeAccessObject:
        return cls.for_class(ChangeRecord)

    def record(
                self, obj: Any, change_type: Union[ChangeType, str], user: User,
                description: str,
            ) -> ChangeRecord:
        if isinstance(change_type, str):
            change_type = ChangeType[change_type]
        return self.klass_.log_change(obj, change_type, user, description)


directory = AccessObject.for_class(Directory)
category = AccessObject.for_class(Category)
page = AccessObject.for_class(Page)
user = UserAccessObject.make()
change = ChangeAccessObject.make()