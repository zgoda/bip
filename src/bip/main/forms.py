from wtforms.fields import BooleanField, StringField

from ..utils.forms import BaseForm, Button


class SearchForm(BaseForm):
    q = StringField('wyszukaj')
    pages = BooleanField('strony', default=True)
    labels = BooleanField('etykiety', default=True)
    attachments = BooleanField('załączniki', default=True)

    buttons = [
        Button(text='szukaj')
    ]
