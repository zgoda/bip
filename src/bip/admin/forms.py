from wtforms.ext.sqlalchemy.fields import QuerySelectField
from wtforms.fields import BooleanField, StringField, TextAreaField
from wtforms_components.fields import EmailField
from wtforms_components.fields.html5 import IntegerField
from wtforms_components.validators import Email

from ..data import Filter, Sort, directory, page
from ..utils.forms import ObjectForm


class UserForm(ObjectForm):
    email = EmailField('email', validators=[Email()])
    active = BooleanField('aktywny')
    admin = BooleanField('administrator')


def directory_query():
    return directory.query(
        sort=[Sort('title')],
        filters=[Filter('active', 'eq', True), Filter('parent_pk', 'is_null')],
    )


def page_query():
    return page.query(sort=[Sort('title')], filters=[Filter('active', 'eq', True)])


class CategoryForm(ObjectForm):
    title = StringField('tytuł')
    description = TextAreaField('opis')
    active = BooleanField('aktywna')
    menu_order = IntegerField('porządek w menu')
    is_directory = BooleanField('jest katalogiem')
    directory = QuerySelectField(
        'katalog', query_factory=directory_query, get_label='title',
        allow_blank=True,
    )
    has_page = BooleanField('ma stronę')
    page = QuerySelectField(
        'strona', query_factory=page_query, get_label='title',
        allow_blank=True,
    )
