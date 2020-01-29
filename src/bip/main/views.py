from flask import render_template

from . import main_bp

from ..data import page


@main_bp.route('/')
def home():
    return render_template('main/index.html')


@main_bp.route('/podstawowe')
def basic_information():
    return render_template('main/basic_information.html')


@main_bp.route('/pracownicy')
def staff():
    return render_template('main/staff.html')


@main_bp.route('/kontakt')
def contact():
    return render_template('main/contact.html')


@main_bp.route('/<int:page_id>', endpoint='page')
def page_view(page_id: int):
    page_obj = page.get(page_id, abort_on_none=True)
    return render_template('main/page.html', page=page_obj)
