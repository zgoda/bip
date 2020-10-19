from __future__ import annotations

import os
from datetime import datetime

import peewee
from flask_login import UserMixin
from passlib.context import CryptContext
from peewee import (
    AutoField, BooleanField, CharField, DateTimeField, ForeignKeyField, IntegerField,
    TextField,
)

from .utils.text import slugify

passwd_ctx = CryptContext(schemes=['bcrypt'])


def generate_password_hash(password: str) -> str:  # pragma: nocover
    return passwd_ctx.hash(password)


def check_password_hash(stored: str, password: str) -> bool:  # pragma: nocover
    return passwd_ctx.verify(password, stored)


DB_DRIVER_MAP = {
    'postgres': peewee.PostgresqlDatabase,
    'mysql': peewee.MySQLDatabase,
    'sqlite': peewee.SqliteDatabase,
}


def get_db_driver():
    name = os.getenv('DB_DRIVER')
    if name:
        name = name.strip()
    if not name:
        name = 'sqlite'
    name = name.lower()
    return name


def _get_db_driver_class():
    name = get_db_driver()
    return DB_DRIVER_MAP[name]


collate_kw = {}


def setup_db_collation(database):  # pragma: nocover
    driver = get_db_driver()
    if driver == 'sqlite':
        import icu
        pl_coll = icu.Collator.createInstance(icu.Locale('pl_PL.utf-8'))

        @database.collation('PL')
        def collate_pl(s1, s2):
            return pl_coll.compare(s1, s2)

        collate_kw['collation'] = 'PL'


db = _get_db_driver_class()(None)

setup_db_collation(db)


class Change:
    created = 1
    updated = 2
    deleted = 3


class Model(peewee.Model):
    class Meta:
        database = db


class User(Model, UserMixin):
    pk = AutoField(primary_key=True)
    name = CharField(max_length=200, unique=True, **collate_kw)
    email = CharField(max_length=200, null=True)
    password = TextField(null=False)
    active = BooleanField(default=True, index=True)
    created = DateTimeField(default=datetime.utcnow)
    admin = BooleanField(default=False)

    def __int__(self) -> int:
        return self.pk

    def get_id(self) -> str:
        return str(self.pk)

    def is_active(self) -> bool:  # pragma: nocover
        return self.active

    def set_password(self, password: str):
        self.password = generate_password_hash(password)

    def check_password(self, password: str) -> bool:
        return check_password_hash(self.password, password)


class Label(Model):
    pk = AutoField(primary_key=True)
    name = CharField(max_length=200, unique=True, **collate_kw)
    slug = CharField(max_length=200, index=True)
    description = TextField(null=True)
    description_html = TextField(null=True)


class Page(Model):
    pk = AutoField(primary_key=True)
    title = CharField(max_length=200, unique=True, **collate_kw)
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
    title = CharField(max_length=200, index=True, **collate_kw)
    description = TextField(null=True)
    description_html = TextField(null=True)

    @property
    def file_save_as(self) -> str:
        _, ext = os.path.splitext(self.filename)
        return f'{slugify(self.title)}{ext}'
