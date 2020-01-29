from functools import lru_cache
from typing import List

from flask import url_for

from ..data import Filter, Sort, page
from ..models import Page
from ..utils.menu import MenuItem


@lru_cache(maxsize=2)
def editor_tools() -> List[MenuItem]:
    return [
        MenuItem('profil', url_for('user.profile')),
        MenuItem('hasło', url_for('user.password_change')),
        MenuItem('wyloguj', url_for('auth.logout')),
    ]


@lru_cache(maxsize=2)
def admin_tools() -> List[MenuItem]:
    return [
        MenuItem('administracja', url_for('admin.home')),
    ]


def page_links() -> List[MenuItem]:
    base_filters = [
        Filter('active', 'eq', True), Filter('main', 'eq', True)
    ]
    nonnull_filters = [Filter('order', 'is_not_null')] + base_filters
    null_filters = [Filter('order', 'is_null')] + base_filters
    order = Sort('title')
    cols = [Page.title, Page.pk]
    q_non_nulls = page.query(filters=nonnull_filters, sort=[order]).values(*cols)
    q_nulls = page.query(filters=null_filters, sort=[order]).values(*cols)
    # order by NULLS LAST supported by PostgreSQL and SQLite >= 3.30 only
    for q in (q_non_nulls, q_nulls):
        for title, pk in q:
            yield MenuItem(title, url_for('main.page', page_id=pk))
