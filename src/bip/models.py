import datetime

from flask_login import UserMixin

from .ext import db


class User(db.Model, UserMixin):
    pk = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Text, nullable=False)
    remote_user_id = db.Column(db.String(200), index=True)
    active = db.Column(db.Boolean, default=True)
    created = db.Column(db.DateTime, default=datetime.datetime.utcnow())

    def is_active(self):
        return self.active
