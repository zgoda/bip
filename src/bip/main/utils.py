from typing import List

from flask import url_for
from flask_sqlalchemy import BaseQuery

from ..data import Filter, Sort, category
from ..utils.menu import MenuItem, VisibilityOptions


def menu_items() -> BaseQuery:
    filters = [Filter(field='active', op='eq', value=True)]
    sort = [
        Sort(field='menu_order'),
        Sort(field='title'),
    ]
    return category.query(sort, filters=filters)


def menu_tools() -> List[MenuItem]:
    return [
        MenuItem(
            'zaloguj', url_for('auth.login'), VisibilityOptions(True, False),
        ),
        MenuItem(
            'profil', url_for('user.profile'), VisibilityOptions(False, True),
        ),
        MenuItem(
            'hasło', url_for('user.password_change'), VisibilityOptions(False, True),
        ),
        MenuItem(
            'wyloguj', url_for('auth.logout'), VisibilityOptions(False, True),
        ),
    ]


def admin_tools() -> List[MenuItem]:
    return [
        MenuItem(
            'administracja', url_for('admin.home'), VisibilityOptions(False, True),
        ),
    ]
