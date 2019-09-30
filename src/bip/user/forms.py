from flask_wtf import FlaskForm
from wtforms.fields import PasswordField
from wtforms.validators import DataRequired
from wtforms_components.fields import EmailField
from wtforms_components.validators import Email

from ..models import User
from ..utils.forms import ObjectForm


class ProfileForm(ObjectForm):
    email = EmailField('email', validators=[Email()])


class ChangePasswordForm(FlaskForm):
    current_password = PasswordField('obecne hasło', validators=[DataRequired()])
    new_password = PasswordField('nowe hasło', validators=[DataRequired()])
    new_password_repeat = PasswordField(
        'nowe hasło (powtórz)', validators=[DataRequired()]
    )

    def save(self, user: User) -> bool:
        if user.check_password(self.current_password.data):
            if self.new_password.data == self.new_password_repeat.data:
                user.set_password(self.new_password.data)
                return True
        return False
