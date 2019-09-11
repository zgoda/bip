from flask import render_template

from . import main_bp


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
