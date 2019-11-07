from typing import Optional

from flask_wtf import FlaskForm
from wtforms.fields import PasswordField, StringField
from wtforms.validators import DataRequired

from ..data import user
from ..models import User
from ..utils.forms import Button


class LoginForm(FlaskForm):
    username = StringField('nazwa użytkownika', validators=[DataRequired()])
    password = PasswordField('hasło', validators=[DataRequired()])

    buttons = [
        Button(text='zaloguj', icon='sign-in-alt')
    ]

    def save(self) -> Optional[User]:
        user_obj = user.by_name(self.username.data)
        if user_obj is not None and user_obj.check_password(self.password.data):
            return user_obj
        return None
