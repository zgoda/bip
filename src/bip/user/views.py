from flask import render_template
from flask_login import login_required

from . import user_bp


@user_bp.route('/profile', methods=['POST', 'GET'])
@login_required
def profile():
    return render_template('user/profile.html')
