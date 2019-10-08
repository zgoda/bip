from typing import List, Optional

from sqlalchemy_filters import apply_filters, apply_sort

from ..ext import db
from ..models import User
from . import Filter, Sort


def create(
            name: str, password: str, email: Optional[str] = None,
            active: bool = False, admin: bool = False,
        ) -> User:
    """Create and return :class:`~bip.models.User` object.

    :param name: user name
    :type name: str
    :param password: password
    :type password: str
    :param email: email, defaults to None
    :type email: str, optional
    :param active: should the account be created active, defaults to False
    :type active: bool, optional
    :param admin: should user have administrative privileges, defaults to
                  False
    :type admin: bool, optional
    :return: user object
    :rtype: :class:`~bip.models.User`
    """
    user = User(name=name, email=email, active=active, admin=admin)
    user.set_password(password)
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
    return User.query.get_or_404(pk)


def query(sort: Optional[List[Sort]] = None, filters: Optional[List[Filter]] = None):
    q = User.query
    if filters:
        q = apply_filters(q, [f._asdict() for f in filters])
    if sort:
        q = apply_sort(q, [s._asdict() for s in sort])
    return q
