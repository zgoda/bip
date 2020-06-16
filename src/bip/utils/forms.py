from dataclasses import dataclass
from typing import ClassVar

import validators
from flask import Markup, render_template_string
from flask_wtf import FlaskForm
from peewee import Model
from wtforms.fields import Field
from wtforms.validators import ValidationError


class Renderable:
    """An object that can be rendered
    """

    def render(self) -> Markup:
        """Render template into :class:`Markup` object.

        :return: rendering result as Markup
        :rtype: Markup
        """
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


class BaseForm(FlaskForm):

    buttons = [
        Button(text='zapisz'),
        Link(href='javascript:history.back()', text='powrót'),
    ]


class ObjectForm(BaseForm):

    def save(self, obj: Model, save: bool = True) -> Model:
        self.populate_obj(obj)
        if save:
            obj.save()
        return obj


class EmailValidator:

    def __init__(self, message=None):
        if message is None:
            message = 'Nieprawidłowy adres email'
        self.message = message

    def __call__(self, form: FlaskForm, field: Field):
        if not validators.email(field.data):
            raise ValidationError(self.message)
