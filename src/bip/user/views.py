from flask import flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required

from . import user_bp
from .forms import ChangePasswordForm, ProfileForm


@user_bp.route('/profile', methods=['POST', 'GET'])
@login_required
def profile():
    form = None
    if request.method == 'POST':
        form = ProfileForm()
        if form.validate_on_submit():
            form.save(obj=current_user)
            flash(
                f'dane użytkownika {current_user.name} zostały zmienione',
                category='success',
            )
            return redirect(request.path)
    ctx = {
        'form': form or ProfileForm(obj=current_user),
    }
    return render_template('user/profile.html', **ctx)


@user_bp.route('/password', methods=['POST', 'GET'])
@login_required
def password_change():
    form = None
    if request.method == 'POST':
        form = ChangePasswordForm()
        if form.validate_on_submit():
            form.save(current_user)
            flash(
                f'hasło użytkownika {current_user.name} zostało pomyślnie zmienione',
                category='success',
            )
            return redirect(url_for('user.profile'))
    ctx = {
        'form': form or ChangePasswordForm()
    }
    return render_template('user/password.html', **ctx)
