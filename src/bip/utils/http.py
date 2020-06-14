from typing import Any, Optional

from flask import abort


def or_404(obj: Optional[Any]) -> Any:
    """Abort with 404 if passed object is None.

    :param obj: something to be checked for None
    :type obj: Optional[Any]
    :return: passed object if it's not None
    :rtype: Any
    """
    if obj is None:
        abort(404)
    return obj
