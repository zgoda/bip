from typing import Optional
from flask_sqlalchemy import BaseQuery
from wtforms.fields import BooleanField, StringField, TextAreaField
from wtforms.fields.html5 import EmailField
from wtforms.validators import InputRequired
from flask_login import current_user

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

    def save(self, obj: Optional[Page] = None) -> Page:
        if obj is None:
            obj = Page(created_by=current_user)
        return super().save(obj)
