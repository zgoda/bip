from ..ext import db
from ..models import Directory


def create(save=True, **kwargs):
    d = Directory(**kwargs)
    if save:
        db.session.add(d)
        db.session.commit()
    return d
