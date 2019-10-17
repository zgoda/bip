from flask import abort


def or_404(obj):
    if obj is None:
        abort(404)
    return obj
