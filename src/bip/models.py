from __future__ import annotations

import os
from datetime import datetime

import peewee
from flask_login import UserMixin
from peewee import (
    AutoField, BooleanField, CharField, DateTimeField, ForeignKeyField, IntegerField,
    TextField,
)
from werkzeug.security import check_password_hash, generate_password_hash

from .utils.text import slugify

DB_DRIVER_MAP = {
    'postgres': peewee.PostgresqlDatabase,
    'mysql': peewee.MySQLDatabase,
    'sqlite': peewee.SqliteDatabase,
}


def _get_db_driver_class():  # pragma: nocover
    name = os.getenv('DB_DRIVER')
    if name is None:
        name = 'sqlite'
    name = name.lower()
    return DB_DRIVER_MAP[name]


db = _get_db_driver_class()(None)


class Change:
    created = 1
    updated = 2
    deleted = 3


class Model(peewee.Model):
    class Meta:
        database = db


class User(Model, UserMixin):
    pk = AutoField(primary_key=True)
    name = CharField(max_length=200, unique=True)
    email = CharField(max_length=200, null=True)
    password = TextField(null=False)
    active = BooleanField(default=True, index=True)
    created = DateTimeField(default=datetime.utcnow)
    admin = BooleanField(default=False)

    def __int__(self):
        return self.pk

    def get_id(self):
        return str(self.pk)

    def is_active(self):  # pragma: nocover
        return self.active

    def set_password(self, password):
        self.password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password, password)


class Label(Model):
    pk = AutoField(primary_key=True)
    name = CharField(max_length=200, unique=True)
    slug = CharField(max_length=200, index=True)
    description = TextField(null=True)
    description_html = TextField(null=True)


class Page(Model):
    pk = AutoField(primary_key=True)
    title = CharField(max_length=200, unique=True)
    slug = CharField(max_length=200, index=True)
    text = TextField()
    text_html = TextField()
    created_by = ForeignKeyField(User, backref='pages_created')
    updated_by = ForeignKeyField(User, backref='pages_updated')
    description = TextField(null=True)
    active = BooleanField(default=True)
    main = BooleanField(default=True)
    order = IntegerField(null=True)
    created = DateTimeField(default=datetime.utcnow)
    updated = DateTimeField(default=datetime.utcnow)

    def labels(self, order=None):
        q = (
            PageLabel.select(PageLabel, Label)
            .join(Label)
            .switch(PageLabel)
            .where(PageLabel.page == self)
        )
        if order is not None:
            q = q.order_by(order)
        return q


class PageLabel(Model):
    pk = AutoField(primary_key=True)
    page = ForeignKeyField(Page)
    label = ForeignKeyField(Label)


class ChangeRecord(Model):
    pk = AutoField(primary_key=True)
    page = ForeignKeyField(Page, backref='changes')
    change_dt = DateTimeField(default=datetime.utcnow, index=True)
    change_type = IntegerField()
    description = TextField()
    user = ForeignKeyField(User, backref='changes')

    @classmethod
    def log_change(
                cls, page: Page, change_type: Change, user: User, description: str
            ) -> ChangeRecord:
        return cls.create(
            page=page, user=user, description=description, change_type=change_type,
        )

    @property
    def change_type_name(self):
        if self.change_type == Change.created:
            return 'utworzenie strony'
        return 'zmiana treści strony'


class Attachment(Model):
    pk = AutoField(primary_key=True)
    page = ForeignKeyField(Page, backref='attachments')
    filename = CharField(max_length=200)
    file_type = CharField(max_length=100)
    file_size = IntegerField()
    created = DateTimeField(default=datetime.utcnow, index=True)
    title = CharField(max_length=200, index=True)
    description = TextField(null=True)
    description_html = TextField(null=True)

    @property
    def file_save_as(self):
        _, ext = os.path.splitext(self.filename)
        return f'{slugify(self.title)}{ext}'
