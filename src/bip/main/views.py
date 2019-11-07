from flask import render_template, Response

from ..data import category
from ..utils.http import or_404
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


@main_bp.route('/kategoria/<int:category_pk>', endpoint='category')
def category_display(category_pk: int) -> Response:
    cat_obj = or_404(category.get(category_pk))
    context = {
        'category': cat_obj,
    }
    return render_template('main/category.html', **context)
