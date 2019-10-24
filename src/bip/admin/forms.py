from wtforms.ext.sqlalchemy.fields import QuerySelectField
from wtforms.fields import BooleanField, StringField, TextAreaField
from wtforms_components.fields import EmailField
from wtforms_components.fields.html5 import IntegerField
from wtforms_components.validators import Email

from ..data import Sort, directory, page
from ..models import Directory, Page
from ..utils.forms import ObjectForm


class UserForm(ObjectForm):
    email = EmailField('email', validators=[Email()])
    active = BooleanField('aktywny')
    admin = BooleanField('administrator')


def directory_query():
    return directory.query(sort=[Sort('title')])


def directory_display(obj: Directory) -> str:
    if obj.active:
        return obj.title
    return f'{obj.title} (nieaktywny)'


def page_query():
    return page.query(sort=[Sort('title')])


def page_display(obj: Page) -> str:
    if obj.active:
        return obj.title
    return f'{obj.title} (nieaktywna)'


class CategoryForm(ObjectForm):
    title = StringField('tytuł')
    description = TextAreaField('opis')
    active = BooleanField('aktywna')
    menu_order = IntegerField('porządek w menu')
    directory = QuerySelectField(
        'katalog', query_factory=directory_query, get_label=directory_display,
        allow_blank=True,
    )
    page = QuerySelectField(
        'strona', query_factory=page_query, get_label=page_display,
        allow_blank=True,
    )
