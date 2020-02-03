from flask import render_template

from ..models import Page, User, ChangeRecord
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


@main_bp.route('/<int:page_id>', endpoint='page')
def page_view(page_id: int):
    Author = User.alias()  # noqa: N806
    Editor = User.alias()  # noqa: N806
    page_obj = or_404(
        Page
        .select(Page, Author, Editor, ChangeRecord)
        .join(Author, on=(Page.created_by == Author.pk))
        .switch(Page)
        .join(Editor, on=(Page.updated_by == Editor.pk))
        .switch(Page)
        .join(ChangeRecord)
        .where(Page.pk == page_id)
        .get()
    )
    return render_template(
        'main/page.html', page=page_obj, change_order=ChangeRecord.change_dt.desc()
    )
