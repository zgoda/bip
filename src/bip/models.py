import datetime
import enum

from flask_login import UserMixin
from markdown2 import markdown

from .ext import db
from .security import pwd_context
from .utils.db import Timestamp
from .utils.text import slugify, truncate_string


class ObjectType(enum.Enum):
    directory = 1
    page = 2
    category = 3


class ChangeType(enum.Enum):
    created = 1
    updated = 2
    deleted = 3


class User(db.Model, UserMixin):
    __tablename__ = 'users'
    pk = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Text, nullable=False)
    remote_user_id = db.Column(db.String(200), index=True)
    email = db.Column(db.String(200))
    password = db.Column(db.Text)
    active = db.Column(db.Boolean, default=True, index=True)
    created = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    admin = db.Column(db.Boolean, default=False, index=True)

    def is_active(self):  # pragma: no cover
        return self.active

    def set_password(self, password):
        self.password = pwd_context.hash(password)

    def check_password(self, password):
        return pwd_context.verify(password, self.password)


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
        'User', foreign_keys=[created_by_pk],
        backref=db.backref('directories_created', lazy='dynamic'),
    )
    updated_by_pk = db.Column(db.Integer, db.ForeignKey('users.pk'))
    updated_by = db.relationship(
        'User', foreign_keys=[updated_by_pk],
        backref=db.backref('directories_updated', lazy='dynamic'),
    )
    page_pk = db.Column(db.Integer, db.ForeignKey('page.pk'), nullable=False)
    page = db.relationship(
        'Page', backref=db.backref('directories', lazy='dynamic')
    )
    description = db.Column(db.Text)
    active = db.Column(db.Boolean, default=True, index=True)


class Page(db.Model, Timestamp):
    __tablename__ = 'page'
    pk = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    short_title = db.Column(db.String(100))
    slug = db.Column(db.Text)
    text = db.Column(db.Text, nullable=False)
    text_html = db.Column(db.Text)
    created_by_pk = db.Column(db.Integer, db.ForeignKey('users.pk'), nullable=False)
    created_by = db.relationship(
        'User', foreign_keys=[created_by_pk],
        backref=db.backref('pages_created', lazy='dynamic'),
    )
    updated_by_pk = db.Column(db.Integer, db.ForeignKey('users.pk'))
    updated_by = db.relationship(
        'User', foreign_keys=[updated_by_pk],
        backref=db.backref('pages_updated', lazy='dynamic'),
    )
    description = db.Column(db.Text)
    active = db.Column(db.Boolean, default=True, index=True)


@db.event.listens_for(Page, 'before_insert')
@db.event.listens_for(Page, 'before_update')
def page_before_save(mapper, connection, target: Page):
    target.slug = slugify(target.title)
    target.text_html = markdown(target.text, safe_mode='replace')
    if not target.short_title:
        target.short_title = truncate_string(target.title, 100)


class Category(db.Model, Timestamp):
    __tablename__ = 'category'
    pk = db.Column(db.Integer, primary_key=True)
    directory_pk = db.Column(db.Integer, db.ForeignKey('directory.pk'))
    directory = db.relationship(
        'Directory', backref=db.backref('categories', lazy='dynamic')
    )
    page_pk = db.Column(db.Integer, db.ForeignKey('page.pk'))
    page = db.relationship(
        'Page', backref=db.backref('categories', lazy='dynamic')
    )
    title = db.Column(db.String(100), index=True)
    description = db.Column(db.Text)
    active = db.Column(db.Boolean, default=True, index=True)
    menu_order = db.Column(db.Integer, nullable=False, default=0, index=True)


@db.event.listens_for(Category.active, 'set')
def category_active_change(target: Category, value, oldvalue, initiator):
    if target.directory is not None:
        target.directory.active = value
    if target.page is not None:
        target.page.active = value


class ChangeRecord(db.Model):
    __tablename__ = 'changelog'
    pk = db.Column(db.Integer, primary_key=True)
    object_pk = db.Column(db.Integer, nullable=False)
    object_type = db.Column(db.Enum(ObjectType), nullable=False)
    change_dt = db.Column(
        db.DateTime, default=datetime.datetime.utcnow, nullable=False, index=True
    )
    change_type = db.Column(db.Enum(ChangeType), nullable=False)
    description = db.Column(db.Text, nullable=False)
    user_pk = db.Column(db.Integer, db.ForeignKey('users.pk'))
    user = db.relationship('User', backref=db.backref('changes', lazy='dynamic'))

    __table_args__ = (
        db.Index('ix_changelog_object', 'object_pk', 'object_type'),
    )

    @classmethod
    def log_change(cls, obj, change_type, user, description):
        return cls(
            object_pk=obj.pk, object_type=obj.__tablename__, user=user,
            description=description, change_type=change_type,
        )
