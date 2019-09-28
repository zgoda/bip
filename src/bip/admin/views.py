from flask import abort, render_template
from flask_login import current_user, login_required

from ..models import User
from . import admin_bp
from ..utils.pagination import paginate


@admin_bp.before_request
@login_required
def before_request():
    if not current_user.admin:
        abort(403)


@admin_bp.route('/home')
def home():
    return render_template('admin/index.html')


@admin_bp.route('/users/list')
def user_list():
    query = User.query.order_by(User.name)
    context = {
        'pagination': paginate(query)
    }
    return render_template('admin/user_list.html', **context)
