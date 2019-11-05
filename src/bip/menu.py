from __future__ import annotations

import json
from typing import Optional, Type

from anytree import Node, NodeMixin
from flask_sqlalchemy import BaseQuery

from .data import Filter, Sort, category
from .models import Category

_ITEM_CACHE = {}


class MenuItem(NodeMixin):

    def __init__(self, pk: int, title: str, endpoint: str, parent=None, children=None):
        self.pk = pk
        self.title = title
        self.endpoint = endpoint
        self.parent = parent
        if children:
            self.children = children
        _ITEM_CACHE[self.pk] = self

    def __repr__(self):
        return f'<CategoryMenuItem(pk={self.pk}, title={self.title})>'

    @classmethod
    def for_pk(cls: Type[MenuItem], pk: int) -> MenuItem:
        cat_obj = category.get(pk)
        return cls.for_object(cat_obj)

    @classmethod
    def for_object(cls: Type[MenuItem], cat_obj: Category) -> MenuItem:
        parent = _ITEM_CACHE.get(cat_obj.parent_pk)
        obj = cls(
            pk=cat_obj.pk, title=cat_obj.title,
            endpoint='main.category', parent=parent
        )
        return obj

    @classmethod
    def from_json(cls: Type[MenuItem], s: str) -> MenuItem:
        data = json.loads(s)
        return cls.from_dict(data)

    @classmethod
    def from_dict(cls: Type[MenuItem], data: dict) -> MenuItem:
        if data['parent'] is not None:
            data['parent'] = _ITEM_CACHE.get(data['parent'])
        return cls(**data)

    def to_dict(self) -> dict:
        rv = {}
        rv.update(self.__dict__)
        if self.parent:
            rv['parent'] = self.parent.pk
        return rv

    def to_json(self) -> str:
        return json.dumps(self.to_dict())


class MenuTree:

    def __init__(self, query: Optional[BaseQuery] = None):
        if query is None:
            query = category.query(
                sort=[
                    Sort(field='menu_level'), Sort(field='menu_order'),
                    Sort(field='title'),
                ], filters=[Filter(field='active', op='eq', value=True)]
            )
        self.root = Node('root')
        _ITEM_CACHE[None] = self.root
        for item in query:
            MenuItem.for_object(item)
