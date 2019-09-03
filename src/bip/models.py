import datetime

from flask_login import UserMixin
from sqlalchemy_utils.models import Timestamp

from .ext import db


class User(db.Model, UserMixin):
    __tablename__ = 'users'
    pk = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Text, nullable=False)
    remote_user_id = db.Column(db.String(200), index=True)
    email = db.Column(db.String(200))
    password = db.Column(db.Text)
    active = db.Column(db.Boolean, default=True)
    created = db.Column(db.DateTime, default=datetime.datetime.utcnow())

    def is_active(self):
        return self.active


class Directory(db.Model, Timestamp):
    __tablename__ = 'directory'
    pk = db.Column(db.Integer, primary_key=True)
    parent_pk = db.Column(db.Integer, db.ForeignKey('directory.pk'))
    name = db.Column(db.String(200))
    children = db.relationship(
        'Directory', backref=db.backref('parent', remote_side=[pk])
    )
    created_by_pk = db.Column(db.Integer, db.ForeignKey('users.pk'), nullable=False)
    created_by = db.relationship(
        'User', backref=db.backref('created_directories', lazy='dynamic')
    )
    updated_by_pk = db.Column(db.Integer, db.ForeignKey('users.pk'))
    updated_by = db.relationship(
        'User', backref=db.backref('updated_directories', lazy='dynamic')
    )
    description = db.Column(db.Text)
    active = db.Column(db.Boolean, default=True)


class Page(db.Model, Timestamp):
    __tablename__ = 'page'
    pk = db.Column(db.Integer, primary_key=True)
    directory_pk = db.Column(db.Integer, db.ForeignKey('directory.pk'))
    directory = db.relationship(
        'Directory', backref=db.backref('pages', lazy='dynamic')
    )
    title = db.Column(db.String(200), nullable=False)
    slug = db.Column(db.Text)
    text = db.Column(db.Text, nullable=False)
    text_html = db.Column(db.Text)
    created_by_pk = db.Column(db.Integer, db.ForeignKey('users.pk'), nullable=False)
    created_by = db.relationship(
        'User', backref=db.backref('created_pages', lazy='dynamic')
    )
    updated_by_pk = db.Column(db.Integer, db.ForeignKey('users.pk'))
    updated_by = db.relationship(
        'User', backref=db.backref('updated_pages', lazy='dynamic')
    )
    description = db.Column(db.Text)
    active = db.Column(db.Boolean, default=True)
