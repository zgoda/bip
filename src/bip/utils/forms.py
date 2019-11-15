from dataclasses import dataclass
from typing import Any, ClassVar, Mapping

from flask import Markup, render_template_string
from flask_wtf import FlaskForm
from flask_sqlalchemy import BaseQuery
from wtforms.fields import BooleanField

from ..ext import db


class Renderable:

    def render(self) -> Markup:
        return Markup(render_template_string(self.template, obj=self))


@dataclass
class Link(Renderable):
    href: str
    text: str = 'klik'

    template: ClassVar[str] = ''.join([
        '<a href="{{ obj.href }}">',
        '{{ obj.text }}',
        '</a>',
    ])


@dataclass
class Button(Renderable):
    type_: str = 'submit'
    class_: str = 'primary'
    icon: str = 'check'
    icon_type: str = 'fas'
    text: str = 'ok'

    template: ClassVar[str] = ''.join([
        '<button type="{{ obj.type_ }}" class="btn btn-{{ obj.class_ }}">',
        '<i class="{{ obj.icon_type }} fa-{{ obj.icon }}"></i>',
        '&nbsp;',
        '{{ obj.text }}',
        '</button>',
    ])


class ConfirmationForm(FlaskForm):
    is_confirmed = BooleanField('potwierdź', default=False)

    buttons = [Button(text='potwierdź')]

    def confirm(self) -> bool:
        if self.is_confirmed.data:
            return True
        return False


class BaseForm(FlaskForm):

    buttons = [
        Button(text='zapisz'),
        Link(href='javascript:history.back()', text='powrót'),
    ]


class ObjectForm(BaseForm):

    def save(self, obj: Any) -> Any:
        self.populate_obj(obj)
        db.session.add(obj)
        db.session.commit()
        return obj


def update_form_queries(form: FlaskForm, queries: Mapping[str, BaseQuery]):
    for field_name, query in queries.items():
        form[field_name].query = query
