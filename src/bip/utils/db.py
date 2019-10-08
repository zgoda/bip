from datetime import datetime

import sqlalchemy as sa
from flask_sqlalchemy.model import Model as BaseModel


class MappedModelMixin:

    __mapper_args__ = {
        'confirm_deleted_rows': False
    }


class Timestamp:
    created = sa.Column(sa.DateTime, default=datetime.utcnow)
    updated = sa.Column(sa.DateTime, onupdate=datetime.utcnow)


class Model(BaseModel, MappedModelMixin):

    def get_id(self):
        return self.pk
