from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Optional, Type

from .data import category
from .models import Category

_ITEM_CACHE = {}


@dataclass
class MenuItem:
    pk: int
    title: str
    endpoint: str
    path: str
    parent: Optional[MenuItem]

    @classmethod
    def for_pk(
                cls: Type[MenuItem], pk: int, parent: Optional[MenuItem] = None
            ) -> MenuItem:
        cat_obj = category.get(pk)
        return cls.for_object(cat_obj, parent)

    @classmethod
    def for_object(
                cls: Type[MenuItem], cat_obj: Category,
                parent: Optional[MenuItem] = None,
            ) -> MenuItem:
        if parent is not None:
            path = f'{parent.path}:{cat_obj.pk}'
        else:
            path = str(cat_obj.pk)
        return cls(
            pk=cat_obj.pk, title=cat_obj.title,
            endpoint='main.category', parent=parent, path=path
        )

    @classmethod
    def from_json(cls: Type[MenuItem], s: str) -> MenuItem:
        data = json.loads(s)
        return cls.from_dict(data)

    @classmethod
    def from_dict(cls: Type[MenuItem], data: dict) -> MenuItem:
        if data['parent'] is not None:
            data['parent'] = _ITEM_CACHE.get(data['parent'])
        return cls(**data)

    def __post_init__(self):
        _ITEM_CACHE[self.pk] = self

    def to_dict(self) -> dict:
        rv = {}
        rv.update(self.__dict__)
        if self.parent:
            rv['parent'] = self.parent.pk
        return rv

    def to_json(self) -> str:
        return json.dumps(self.to_dict())
