from datetime import datetime
from typing import Optional

from flask_login import current_user
from markdown import markdown
from peewee import Query
from wtforms.fields import BooleanField, StringField, TextAreaField
from wtforms.fields.html5 import EmailField, IntegerField
from wtforms.validators import InputRequired, Optional as ValueOptional

from ..models import Page
from ..utils.forms import EmailValidator, ObjectForm
from ..utils.text import slugify


class UserForm(ObjectForm):
    email = EmailField('email', validators=[EmailValidator()])
    active = BooleanField('aktywny')
    admin = BooleanField('administrator')


def page_query() -> Query:
    return Page.select().order_by(Page.title)


def object_display(obj: Page) -> str:
    if obj.active:
        return obj.title
    return f'{obj.title} (nieaktywna)'


class PageForm(ObjectForm):
    order = IntegerField(
        'porządek', validators=[ValueOptional()],
        description='strony bez ustawionego porządku są sortowane na końcu '
        'listy według tytułu'
    )
    title = StringField('tytuł', validators=[InputRequired()])
    text = TextAreaField(
        'tekst', validators=[InputRequired()],
        description='treść strony zapisana przy użyciu Markdown',
    )
    description = TextAreaField('opis')
    active = BooleanField('aktywna')
    main = BooleanField(
        'główna', description='czy strona ma być widoczna na liście stron w menu'
    )

    def save(self, obj: Optional[Page] = None) -> Page:
        if obj is None:
            obj = Page(created_by=current_user)
        page = super().save(obj, False)
        page.updated_by = current_user
        page.updated = datetime.utcnow()
        page.slug = slugify(page.title)
        page.text_html = markdown(page.text)
        page.save()
        return page
