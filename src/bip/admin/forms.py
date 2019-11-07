from typing import Union

from flask_sqlalchemy import BaseQuery
from wtforms.ext.sqlalchemy.fields import QuerySelectField
from wtforms.fields import BooleanField, StringField, TextAreaField
from wtforms.validators import InputRequired
from wtforms_components.fields import EmailField
from wtforms_components.fields.html5 import IntegerField
from wtforms_components.validators import Email

from ..data import Sort, page
from ..models import Category, Page
from ..utils.forms import ObjectForm


class UserForm(ObjectForm):
    email = EmailField('email', validators=[Email()])
    active = BooleanField('aktywny')
    admin = BooleanField('administrator')


def page_query() -> BaseQuery:
    return page.query(sort=[Sort('title')])


def object_display(obj: Union[Category, Page]) -> str:
    if obj.active:
        return obj.title
    return f'{obj.title} (nieaktywna)'


class CategoryForm(ObjectForm):
    title = StringField('tytuł')
    description = TextAreaField('opis')
    active = BooleanField('aktywna')
    menu_order = IntegerField('porządek w menu')
    page = QuerySelectField(
        'strona', query_factory=page_query, get_label=object_display,
        allow_blank=True,
    )
    parent = QuerySelectField(
        'kategoria nadrzędna', get_label=object_display, allow_blank=True
    )


class PageForm(ObjectForm):
    title = StringField('tytuł', validators=[InputRequired()])
    short_title = StringField('krótki tytuł')
    text = TextAreaField(
        'tekst', validators=[InputRequired()],
        description='treść strony zapisana przy użyciu Markdown',
    )
    description = TextAreaField('opis')
    active = BooleanField('aktywna')
