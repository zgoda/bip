import datetime
import enum

from flask_login import UserMixin
from markdown import markdown
from werkzeug.security import check_password_hash, generate_password_hash

from .ext import db
from .utils.db import Timestamp
from .utils.text import slugify, truncate_string


class ChangeType(enum.Enum):
    created = 1
    updated = 2
    deleted = 3


class User(db.Model, UserMixin):
    __tablename__ = 'users'
    pk = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Text, nullable=False)
    email = db.Column(db.String(200))
    password = db.Column(db.Text)
    active = db.Column(db.Boolean, default=True, index=True)
    created = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    admin = db.Column(db.Boolean, default=False, index=True)

    def is_active(self):  # pragma: no cover
        return self.active

    def set_password(self, password):
        self.password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password, password)


page_labels = db.Table(
    'page_labels',
    db.Column('page_pk', db.Integer, db.ForeignKey('page.pk'), primary_key=True),
    db.Column('label_pk', db.Integer, db.ForeignKey('label.pk'), primary_key=True),
)


class Label(db.Model):
    __tablename__ = 'label'
    pk = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False, index=True)
    slug = db.Column(db.String(200), index=True)
    description = db.Column(db.Text)
    description_html = db.Column(db.Text)


@db.event.listens_for(Label, 'before_insert')
@db.event.listens_for(Label, 'before_update')
def label_before_save(mapper, connection, target: Label):
    target.slug = slugify(target.name)
    target.description_html = markdown(target.dexcription, output_format='html5')


class Page(db.Model, Timestamp):
    __tablename__ = 'page'
    pk = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    short_title = db.Column(db.String(100))
    slug = db.Column(db.String(200), index=True)
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
    main = db.Column(db.Boolean, default=True, index=True)
    order = db.Column(db.Integer, index=True)
    labels = db.relationship(
        'Label', secondary=page_labels, lazy='subquery',
        backref=db.backref('pages', lazy=True),
    )

    def __repr__(self):
        return self.title


@db.event.listens_for(Page, 'before_insert')
@db.event.listens_for(Page, 'before_update')
def page_before_save(mapper, connection, target: Page):
    target.slug = slugify(target.title)
    target.text_html = markdown(target.text, output_format='html5')
    if not target.short_title:
        target.short_title = truncate_string(target.title, 100)


class ChangeRecord(db.Model):
    __tablename__ = 'changelog'
    pk = db.Column(db.Integer, primary_key=True)
    page_pk = db.Column(db.Integer, db.ForeignKey('page.pk'), nullable=False)
    page = db.relationship('Page', backref=db.backref('changes', lazy='dynamic'))
    change_dt = db.Column(
        db.DateTime, default=datetime.datetime.utcnow, nullable=False, index=True
    )
    change_type = db.Column(db.Enum(ChangeType), nullable=False)
    description = db.Column(db.Text, nullable=False)
    user_pk = db.Column(db.Integer, db.ForeignKey('users.pk'))
    user = db.relationship('User', backref=db.backref('changes', lazy='dynamic'))

    @classmethod
    def log_change(cls, page, change_type, user, description):
        return cls(
            page_pk=page.pk, user=user, description=description,
            change_type=change_type,
        )
