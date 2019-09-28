from wtforms.fields import HiddenField

from .._version import get_version
from ..utils.pagination import url_for_other_page
from ..utils.text import yesno


def extra_context(**kwargs):
    extra = {
        'version': get_version(),
        'is_hidden_field': lambda x: isinstance(x, HiddenField),
        'url_for_other_page': url_for_other_page,
    }
    extra.update(kwargs)
    return extra


def extra_filters(**kwargs):
    extra = {
        'yesno': yesno,
    }
    extra.update(kwargs)
    return extra
