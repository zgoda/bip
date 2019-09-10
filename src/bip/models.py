import datetime
import enum

from flask_login import UserMixin
from sqlalchemy_utils.models import Timestamp

from .ext import db


class ObjectType(enum.Enum):
    directory = 1
    page = 2
    category = 3


class User(db.Model, UserMixin):
    __tablename__ = 'users'
    pk = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Text, nullable=False)
    remote_user_id = db.Column(db.String(200), index=True)
    email = db.Column(db.String(200))
    password = db.Column(db.Text)
    active = db.Column(db.Boolean, default=True, index=True)
    created = db.Column(db.DateTime, default=datetime.datetime.utcnow())

    def is_active(self):
        return self.active


class Directory(db.Model, Timestamp):
    __tablename__ = 'directory'
    pk = db.Column(db.Integer, primary_key=True)
    parent_pk = db.Column(db.Integer, db.ForeignKey('directory.pk'))
    title = db.Column(db.String(200), nullable=False)
    short_title = db.Column(db.String(100))
    children = db.relationship(
        'Directory', backref=db.backref('parent', remote_side=[pk])
    )
    created_by_pk = db.Column(db.Integer, db.ForeignKey('users.pk'), nullable=False)
    created_by = db.relationship(
        'User', backref=db.backref('directories_created', lazy='dynamic')
    )
    updated_by_pk = db.Column(db.Integer, db.ForeignKey('users.pk'))
    updated_by = db.relationship(
        'User', backref=db.backref('directories_updated', lazy='dynamic')
    )
    description = db.Column(db.Text)
    active = db.Column(db.Boolean, default=True, index=True)


class SubjectPage(db.Model, Timestamp):
    __tablename__ = 'page'
    pk = db.Column(db.Integer, primary_key=True)
    directory_pk = db.Column(db.Integer, db.ForeignKey('directory.pk'))
    directory = db.relationship(
        'Directory', backref=db.backref('pages', lazy='dynamic')
    )
    title = db.Column(db.String(200), nullable=False)
    short_title = db.Column(db.String(100))
    slug = db.Column(db.Text)
    text = db.Column(db.Text, nullable=False)
    text_html = db.Column(db.Text)
    created_by_pk = db.Column(db.Integer, db.ForeignKey('users.pk'), nullable=False)
    created_by = db.relationship(
        'User', backref=db.backref('pages_created', lazy='dynamic')
    )
    updated_by_pk = db.Column(db.Integer, db.ForeignKey('users.pk'))
    updated_by = db.relationship(
        'User', backref=db.backref('pages_updated', lazy='dynamic')
    )
    description = db.Column(db.Text)
    active = db.Column(db.Boolean, default=True, index=True)


class ObjectMenuItem(db.Model, Timestamp):
    __tablename__ = 'category'
    pk = db.Column(db.Integer, primary_key=True)
    directory_pk = db.Column(db.Integer, db.ForeignKey('directory.pk'))
    directory = db.relationship(
        'Directory', backref=db.backref('categories', lazy='dynamic')
    )
    page_pk = db.Column(db.Integer, db.ForeignKey('page.pk'))
    page = db.relationship('Page', backref=db.backref('categories', lazy='dynamic'))
    title = db.Column(db.String(100), index=True)
    description = db.Column(db.Text)
    active = db.Column(db.Boolean, default=True, index=True)
    menu_order = db.Column(db.Integer, nullable=False, default=0, index=True)


class ChangeRegistry(db.Model):
    __tablename__ = 'changelog'
    pk = db.Column(db.Integer, primary_key=True)
    object_pk = db.Column(db.Integer, nullable=False, index=True)
    object_type = db.Column(db.Enum(ObjectType))
    change_dt = db.Column(
        db.DateTime, default=datetime.datetime.utcnow, nullable=False, index=True
    )
    description = db.Column(db.Text, nullable=False)