from ..ext import db
from ..models import Directory


def create(save=True, **kwargs):
    c = Directory(**kwargs)
    if save:
        db.session.add(c)
        db.session.commit()
