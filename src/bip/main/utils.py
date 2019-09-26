from flask import url_for

from ..models import ObjectMenuItem
from ..utils.views import MenuTool


def menu_items():
    q = ObjectMenuItem.query.filter_by(
        active=True
    ).order_by(ObjectMenuItem.menu_order, ObjectMenuItem.title)
    return q


def menu_tools():
    return [
        MenuTool(
            'logowanie', url_for('auth.login'),
            hide_authenticated=True, hide_anonymous=False,
        ),
        MenuTool(
            'wyloguj', url_for('auth.logout'),
            hide_authenticated=False, hide_anonymous=True,
        )
    ]
