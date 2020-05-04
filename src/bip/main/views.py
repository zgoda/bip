from typing import Union

from flask import Response, render_template

from ..models import ChangeRecord, Label, Page, PageLabel, User
from ..utils.http import or_404
from . import main_bp


@main_bp.route('/')
def home() -> str:
    return render_template('main/index.html')


@main_bp.route('/podstawowe')
def basic_information() -> str:
    return render_template('main/basic_information.html')


@main_bp.route('/pracownicy')
def staff() -> str:
    return render_template('main/staff.html')


@main_bp.route('/kontakt')
def contact() -> str:
    return render_template('main/contact.html')


@main_bp.route('/<int:page_id>', endpoint='page')
def page_view(page_id: int) -> Union[str, Response]:
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
        .peek()
    )
    return render_template(
        'main/page.html', page=page_obj, change_order=ChangeRecord.change_dt.desc()
    )


@main_bp.route('/label/<slug>')
def label_page_list(slug: str) -> str:
    label = or_404(Label.get(Label.slug == slug))
    pages = (
        Page
        .select()
        .join(PageLabel)
        .where(PageLabel.label == label)
        .order_by(Page.title)
    )
    ctx = {
        'label': label,
        'label_pages': pages,
        'num_pages': pages.count(),
    }
    return render_template('main/label_page_list.html', **ctx)
