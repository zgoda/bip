from typing import Any, Optional

from flask import abort


def or_404(obj: Optional[Any]) -> Any:
    if obj is None:
        abort(404)
    return obj
