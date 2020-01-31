from flask import render_template
from playhouse.flask_utils import get_object_or_404

from ..models import Page
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


@main_bp.route('/<int:page_id>', endpoint='page')
def page_view(page_id: int):
    page_obj = get_object_or_404(Page, Page.pk == page_id)
    return render_template('main/page.html', page=page_obj)
