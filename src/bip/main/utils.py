from functools import lru_cache
from typing import Generator, List

from flask import url_for
from peewee import ModelSelect, fn

from ..models import Label, Page, PageLabel
from ..utils.menu import MenuItem


@lru_cache(maxsize=2)
def editor_tools() -> List[MenuItem]:
    """Content editor menu items.

    :return: list of menu items
    :rtype: List[MenuItem]
    """
    return [
        MenuItem('profil', url_for('user.profile')),
        MenuItem('hasło', url_for('user.password_change')),
        MenuItem('wyloguj', url_for('auth.logout')),
    ]


@lru_cache(maxsize=2)
def admin_tools() -> List[MenuItem]:
    """Admin tools menu items.

    :return: list of menu items
    :rtype: List[MenuItem]
    """
    return [
        MenuItem('administracja', url_for('admin.home')),
    ]


def page_links() -> Generator[MenuItem, None, None]:
    """Links to pages to be displayed as menu items.

    :yield: menu item
    :rtype: Generator[MenuItem, None, None]
    """
    base_filters = (Page.active == True) & (Page.main == True)  # noqa: E712
    nonnull_filters = Page.order.is_null(False) & base_filters
    null_filters = Page.order.is_null(True) & base_filters
    cols = [Page.title, Page.slug]
    q_non_nulls = Page.select(*cols).where(nonnull_filters).order_by(Page.order)
    q_nulls = Page.select(*cols).where(null_filters).order_by(Page.title)
    # order by NULLS LAST is supported only by PostgreSQL and SQLite >= 3.30 so
    # we have to do it this way
    for q in (q_non_nulls, q_nulls):
        for title, slug in q.tuples():
            yield MenuItem(title, url_for('main.page', slug=slug))


def labels() -> ModelSelect:
    """Function returns query over labels annotated with count of pages. Only
    labels that have any page are returned.

    :return: Label query object
    :rtype: peewee.ModelSelect
    """
    return (
        Label.select(Label, fn.Count(PageLabel.pk).alias('page_count'))
        .join(PageLabel)
        .group_by(Label)
        .order_by(Label.name)
    )
