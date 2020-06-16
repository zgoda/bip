from typing import Union

from flask import Response, render_template, request

from ..models import ChangeRecord, Label, Page, PageLabel, User
from ..search import search_results
from ..utils.http import or_404
from ..utils.pagination import paginate
from . import main_bp
from .forms import SearchForm


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


@main_bp.route('/zmiany')
def changes() -> str:
    change_list = (
        ChangeRecord.select(ChangeRecord, Page, User)
        .join(Page)
        .switch(ChangeRecord)
        .join(User)
        .order_by(ChangeRecord.change_dt.desc())
    )
    ctx = {
        'pagination': paginate(change_list, size=10),
    }
    return render_template('main/changes.html', **ctx)


@main_bp.route('/<slug>', endpoint='page')
def page_view(slug: str) -> Union[str, Response]:
    Author = User.alias()  # noqa: N806
    Editor = User.alias()  # noqa: N806
    page_obj = or_404(
        Page.select(Page, Author, Editor, ChangeRecord)
        .join(Author, on=(Page.created_by == Author.pk))
        .switch(Page)
        .join(Editor, on=(Page.updated_by == Editor.pk))
        .switch(Page)
        .join(ChangeRecord)
        .where(Page.slug == slug)
        .peek()
    )
    return render_template(
        'main/page.html', page=page_obj, change_order=ChangeRecord.change_dt.desc()
    )


@main_bp.route('/etykieta/<slug>')
def label_page_list(slug: str) -> Union[str, Response]:
    label = or_404(Label.get_or_none(Label.slug == slug))
    pages = (
        Page.select()
        .join(PageLabel)
        .where(PageLabel.label == label)
        .order_by(Page.title)
    )
    ctx = {
        'label': label,
        'pagination': paginate(pages, size=10),
        'num_pages': pages.count(),
    }
    return render_template('main/label_page_list.html', **ctx)


@main_bp.route('/szukaj')
def search() -> Union[str, Response]:
    query = request.args.get('q')
    sections = request.args.getlist('d')
    results = None
    if query:
        results = search_results(query, sections=sections)
    form = SearchForm()
    return render_template('main/search.html', query=query, results=results, form=form)
