from wtforms.fields import BooleanField
from wtforms_components.fields import EmailField

from ..utils.forms import ObjectForm


class UserForm(ObjectForm):
    email = EmailField('email')
    active = BooleanField('aktywny')
    admin = BooleanField('administrator')
