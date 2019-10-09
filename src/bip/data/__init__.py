from collections import namedtuple

from ..ext import db


Filter = namedtuple('Filter', 'field,op,value,model', defaults=(None, None))
Sort = namedtuple(
    'Sort', 'field,direction,model,nullsfirst,nullslast',
    defaults=('asc', None, None, None),
)


def create_object(klass, save=True, **kwargs):
    obj = klass(**kwargs)
    if save:
        db.session.add(obj)
        db.session.commit()
    return obj
