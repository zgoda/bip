from flask_wtf import FlaskForm
from wtforms.fields import PasswordField, StringField
from wtforms.validators import DataRequired

from ..models import User
from ..utils.forms import Button


class LoginForm(FlaskForm):
    username = StringField('nazwa użytkownika', validators=[DataRequired()])
    password = PasswordField('hasło', validators=[DataRequired()])

    buttons = [
        Button(text='zaloguj', icon='sign-in-alt')
    ]

    def save(self):
        user = User.query.filter_by(name=self.username.data).first()
        if user is not None and user.check_password(self.password.data):
            return user
        return None
