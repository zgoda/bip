from ..ext import db
from ..models import Page


def create(save=True, **kwargs):
    c = Page(**kwargs)
    if save:
        db.session.add(c)
        db.session.commit()
