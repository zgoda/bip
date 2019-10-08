import attr
from flask import Markup, render_template_string
from flask_wtf import FlaskForm
from wtforms.fields import BooleanField

from ..ext import db


class Renderable:

    def render(self):
        return Markup(render_template_string(self.template, obj=self))


@attr.s
class Link(Renderable):
    href = attr.ib()
    text = attr.ib(default='klik')

    template = ''.join([
        '<a href="{{ obj.href }}">',
        '{{ obj.text }}',
        '</a>',
    ])


@attr.s
class Button(Renderable):
    type_ = attr.ib(default='submit')
    class_ = attr.ib(default='primary')
    icon = attr.ib(default='check')
    icon_type = attr.ib(default='fas')
    text = attr.ib('ok')

    template = ''.join([
        '<button type="{{ obj.type_ }}" class="btn btn-{{ obj.class_ }}">',
        '<i class="{{ obj.icon_type }} fa-{{ obj.icon }}"></i>',
        '&nbsp;',
        '{{ obj.text }}',
        '</button>',
    ])


class ConfirmationForm(FlaskForm):
    is_confirmed = BooleanField('potwierdź', default=False)

    buttons = [Button(text='potwierdź', icon='skull-crossbones')]

    def confirm(self):
        if self.is_confirmed.data:
            return True
        return False


class BaseForm(FlaskForm):

    buttons = [
        Button(text='zapisz'),
        Link(href='javascript:history.back()', text='powrót'),
    ]


class ObjectForm(BaseForm):

    def save(self, obj):
        self.populate_obj(obj)
        db.session.add(obj)
        db.session.commit()
        return obj
