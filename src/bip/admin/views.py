from flask import abort, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required

from ..models import User
from ..utils.pagination import paginate
from . import admin_bp
from .forms import UserForm


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


@admin_bp.route('/users/<int:user_pk>', methods=['POST', 'GET'])
def user_detail(user_pk):
    user = User.query.get_or_404(user_pk)
    form = None
    if request.method == 'POST':
        form = UserForm()
        if form.validate_on_submit():
            user = form.save(obj=user)
            flash(f'dane użytkownika {user.name} zostały zmienione', category='success')
            return redirect(url_for('admin.user_list'))
    context = {
        'user': user,
        'form': form or UserForm(obj=user),
    }
    return render_template('admin/user_detail.html', **context)
