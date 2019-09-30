from flask import render_template, request, flash, redirect
from flask_login import login_required, current_user

from . import user_bp
from .forms import ProfileForm


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
