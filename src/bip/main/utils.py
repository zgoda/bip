from flask import url_for

from ..models import ObjectMenuItem
from ..utils.menu import MenuItem, VisibilityOptions


def menu_items():
    q = ObjectMenuItem.query.filter_by(
        active=True
    ).order_by(ObjectMenuItem.menu_order, ObjectMenuItem.title)
    return q


def menu_tools():
    return [
        MenuItem(
            'zaloguj', url_for('auth.login'), VisibilityOptions(True, False),
        ),
        MenuItem(
            'profil', url_for('user.profile'), VisibilityOptions(False, True),
        ),
        MenuItem(
            'wyloguj', url_for('auth.logout'), VisibilityOptions(False, True),
        ),
    ]


def admin_tools():
    return [
        MenuItem(
            'administracja', url_for('admin.home'), VisibilityOptions(False, True),
        ),
    ]
