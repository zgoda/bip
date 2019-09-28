from wtforms_components.fields import EmailField

from ..utils.forms import ObjectForm


class ProfileForm(ObjectForm):
    email = EmailField('email')
