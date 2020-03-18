from typing import Optional

from flask_wtf import FlaskForm
from wtforms.fields import PasswordField, StringField
from wtforms.validators import InputRequired

from ..models import User
from ..utils.forms import Button


class LoginForm(FlaskForm):
    username = StringField('nazwa użytkownika', validators=[InputRequired()])
    password = PasswordField('hasło', validators=[InputRequired()])

    buttons = [
        Button(text='zaloguj', icon='sign-in-alt')
    ]

    def save(self) -> Optional[User]:
        user_obj = User.get_or_none(User.name == self.username.data)
        if user_obj is not None and user_obj.check_password(self.password.data):
            return user_obj
        return None
