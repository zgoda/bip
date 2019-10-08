from ..ext import db
from ..models import Page


def create(save=True, **kwargs):
    p = Page(**kwargs)
    if save:
        db.session.add(p)
        db.session.commit()
    return p
