from wtforms.fields import HiddenField

from .._version import get_version


def extra_context(**kwargs):
    extra = {
        'version': get_version(),
        'is_hidden_field': lambda x: isinstance(x, HiddenField),
    }
    extra.update(kwargs)
    return extra
