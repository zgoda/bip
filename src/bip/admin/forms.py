from flask_sqlalchemy import BaseQuery
from wtforms.fields import BooleanField, StringField, TextAreaField
from wtforms.fields.html5 import EmailField
from wtforms.validators import InputRequired

from ..data import Sort, page
from ..models import Page
from ..utils.forms import EmailValidator, ObjectForm


class UserForm(ObjectForm):
    email = EmailField('email', validators=[EmailValidator()])
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
