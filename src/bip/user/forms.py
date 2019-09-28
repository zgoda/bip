from wtforms.fields import BooleanField
from wtforms_components.fields import EmailField

from ..utils.forms import ObjectForm


class ProfileForm(ObjectForm):
    email = EmailField('email')


class AdminProfileForm(ObjectForm):
    email = EmailField('email')
    active = BooleanField('aktywny')
    admin = BooleanField('administrator')
