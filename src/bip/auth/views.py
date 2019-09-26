from flask import flash, redirect, render_template, request
from flask_login import login_user

from ..utils.views import next_redirect
from . import auth_bp
from .forms import LoginForm


@auth_bp.route('/login', methods=['POST', 'GET'])
def login():
    form = None
    if request.method == 'POST':
        form = LoginForm()
        if form.validate_on_submit():
            user = form.save()
            if user is None:
                flash('nieprawidłowe dane logowania', category='danger')
                return redirect(request.path)
            login_user(user)
            flash(f'użytkownik {user.name} zalogowany pomyślnie', category='success')
            return redirect(next_redirect('main.home'))
    context = {
        'form': form or LoginForm(),
    }
    return render_template('auth/login.html', **context)
