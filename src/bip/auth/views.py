from flask import Response, flash, redirect, render_template, request, session
from flask_login import current_user, login_required, login_user, logout_user

from ..utils.views import next_redirect
from . import auth_bp
from .forms import LoginForm


@auth_bp.route('/zaloguj', methods=['POST', 'GET'])
def login() -> Response:
    form = LoginForm()
    if form.validate_on_submit():
        user = form.save()
        if user is None:
            flash('nieprawidłowe dane logowania', category='danger')
            return redirect(request.path)
        login_user(user)
        session.permanent = True
        flash(f'użytkownik {user.name} zalogowany pomyślnie', category='success')
        return redirect(next_redirect('main.home'))
    context = {
        'form': form,
    }
    return render_template('auth/login.html', **context)


@auth_bp.route('/wyloguj')
@login_required
def logout() -> Response:
    user_name = current_user.name
    logout_user()
    flash(f'użytkownik {user_name} wylogowany z systemu', category='success')
    return redirect(next_redirect('main.home'))
