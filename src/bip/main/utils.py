from functools import lru_cache
from typing import List

from flask import url_for

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
    base_filters = (Page.active == True) & (Page.main == True)  # noqa: E712
    nonnull_filters = Page.order.is_null(False) & base_filters
    null_filters = Page.order.is_null(True) & base_filters
    cols = [Page.title, Page.pk]
    q_non_nulls = Page.select(*cols).where(nonnull_filters).order_by(Page.order)
    q_nulls = Page.select(*cols).where(null_filters).order_by(Page.title)
    # order by NULLS LAST is supported only by PostgreSQL and SQLite >= 3.30 so
    # we have to do it this way
    for q in (q_non_nulls, q_nulls):
        for title, pk in q.tuples():
            yield MenuItem(title, url_for('main.page', page_id=pk))
