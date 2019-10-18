from typing import List, Optional

from flask_sqlalchemy import BaseQuery

from ..ext import db
from ..models import User
from . import Filter, Sort, create_object, get_query, get_object


def create(save: bool = True, **kwargs) -> User:
    password = kwargs.pop('password')
    user = create_object(User, save=False, **kwargs)
    user.set_password(password)
    if save:
        db.session.add(user)
        db.session.commit()
    return user


def by_name(name: str, **params) -> Optional[User]:
    """Find and return user object that matches specified name and optionally
    other parameters.

    :param name: user name
    :type name: str
    :return: user object or None
    :rtype: :class:`~bip.models.User`
    """
    return User.query.filter_by(name=name, **params).first()


def get_or_404(pk: int) -> User:
    """Get user object or raise HTTP error 404.

    :param pk: user pk
    :type pk: int
    :return: user object
    :rtype: :class:`~bip.models.User`
    """
    return get_object(User, pk, abort_on_none=True)


def query(
            sort: Optional[List[Sort]] = None, filters: Optional[List[Filter]] = None
        ) -> BaseQuery:
    """Build and return query over :class:`~bip.models.User` objects.

    :param sort: list of sort specs, defaults to None
    :type sort: Optional[List[Sort]], optional
    :param filters: list of filter specs, defaults to None
    :type filters: Optional[List[Filter]], optional
    :return: SQLAlchemy query object
    :rtype: :class:`~flask_sqlalchemy.BaseQuery`
    """
    return get_query(User, sort, filters)
