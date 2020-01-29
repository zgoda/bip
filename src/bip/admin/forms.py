from flask_sqlalchemy import BaseQuery
from wtforms.fields import BooleanField, StringField, TextAreaField
from wtforms.validators import InputRequired
from wtforms_components.fields import EmailField
from wtforms_components.validators import Email

from ..data import Sort, page
from ..models import Page
from ..utils.forms import ObjectForm


class UserForm(ObjectForm):
    email = EmailField('email', validators=[Email()])
    active = BooleanField('aktywny')
    admin = BooleanField('administrator')


def page_query() -> BaseQuery:
    return page.query(sort=[Sort('title')])


def object_display(obj: Page) -> str:
    if obj.active:
        return obj.title
    return f'{obj.title} (nieaktywna)'


class PageForm(ObjectForm):
    title = StringField('tytuł', validators=[InputRequired()])
    short_title = StringField('krótki tytuł')
    text = TextAreaField(
        'tekst', validators=[InputRequired()],
        description='treść strony zapisana przy użyciu Markdown',
    )
    description = TextAreaField('opis')
    active = BooleanField('aktywna')
