from wtforms.fields import PasswordField
from wtforms.fields.html5 import EmailField
from wtforms.validators import EqualTo, InputRequired

from ..models import User
from ..utils.forms import BaseForm, EmailValidator, ObjectForm


class ProfileForm(ObjectForm):
    email = EmailField('email', validators=[EmailValidator()])


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
        user.save()
