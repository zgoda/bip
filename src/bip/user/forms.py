from wtforms.fields import PasswordField
from wtforms.validators import EqualTo, InputRequired
from wtforms_components.fields import EmailField
from wtforms_components.validators import Email

from ..ext import db
from ..models import User
from ..utils.forms import BaseForm, ObjectForm


class ProfileForm(ObjectForm):
    email = EmailField('email', validators=[Email()])


class ChangePasswordForm(BaseForm):
    new_password = PasswordField('nowe hasło', validators=[InputRequired()])
    new_password_repeat = PasswordField(
        'nowe hasło (powtórz)',
        validators=[
            InputRequired(),
            EqualTo('new_password', message='Hasła muszą być identyczne'),
        ],
    )

    def save(self, user: User):
        user.set_password(self.new_password.data)
        db.session.add(user)
        db.session.commit()
