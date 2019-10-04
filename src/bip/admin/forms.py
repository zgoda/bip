from wtforms.fields import BooleanField
from wtforms_components.fields import EmailField
from wtforms_components.validators import Email

from ..utils.forms import ObjectForm


class UserForm(ObjectForm):
    email = EmailField('email', validators=[Email()])
    active = BooleanField('aktywny')
    admin = BooleanField('administrator')
