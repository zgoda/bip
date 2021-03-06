from wtforms.fields import HiddenField

from .._version import get_version
from ..utils.pagination import url_for_other_page
from ..utils.text import pluralize, yesno


def extra_context(**kwargs) -> dict:
    """Things to be added to Jinja context.

    :return: extra context
    :rtype: dict
    """
    extra = {
        'version': get_version(),
        'is_hidden_field': lambda x: isinstance(x, HiddenField),
        'url_for_other_page': url_for_other_page,
    }
    extra.update(kwargs)
    return extra


def extra_filters(**kwargs) -> dict:
    """Additional filters to be registered in Jinja environment.

    :return: extra filters
    :rtype: dict
    """
    extra = {
        'yesno': yesno,
        'pluralize': pluralize,
    }
    extra.update(kwargs)
    return extra
