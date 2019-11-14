from __future__ import annotations

from typing import Optional, Sequence, Type

from anytree import Node, NodeMixin
from flask_sqlalchemy import BaseQuery

from .data import Filter, Sort, category
from .models import Category
from .signals import reload_menu_tree

_ITEM_CACHE = {}


class MenuItem(NodeMixin):

    def __init__(
                self, pk: int, title: str, endpoint: str,
                parent: Optional[NodeMixin] = None,
                children: Optional[Sequence] = None,
            ):
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
    def for_object(cls: Type[MenuItem], cat_obj: Category) -> MenuItem:
        parent = _ITEM_CACHE.get(cat_obj.parent_pk)
        obj = cls(
            pk=cat_obj.pk, title=cat_obj.title,
            endpoint='main.category', parent=parent
        )
        return obj


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


@reload_menu_tree.connect
def reload_menu(app, **kwargs):
    app.menu_tree = app.jinja_env.globals['menu_tree'] = MenuTree()
