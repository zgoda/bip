from flask import render_template

from ..data import category
from ..utils.http import or_404
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


@main_bp.route('/kategoria/<int:category_id>', endpoint='category')
def category_display(category_id):
    cat_obj = or_404(category.get(category_id))
    context = {
        'category': cat_obj,
    }
    return render_template('main/category.html', **context)
