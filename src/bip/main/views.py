from flask import render_template, Response

from . import main_bp


@main_bp.route('/')
def home() -> Response:
    return render_template('main/index.html')


@main_bp.route('/podstawowe')
def basic_information() -> Response:
    return render_template('main/basic_information.html')


@main_bp.route('/pracownicy')
def staff() -> Response:
    return render_template('main/staff.html')


@main_bp.route('/kontakt')
def contact() -> Response:
    return render_template('main/contact.html')
