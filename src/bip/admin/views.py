from flask import abort, render_template

from flask_login import login_required, current_user

from . import admin_bp


@admin_bp.before_request
@login_required
def before_request():
    if not current_user.admin:
        abort(401)


@admin_bp.route('/')
def index():
    return render_template('admin/index.html')
