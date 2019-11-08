from typing import Optional

from flask import Response, abort, render_template
from flask_login import current_user, login_required

from ..data import Filter, Sort, category, page, user
from . import admin_bp
from .forms import CategoryForm, PageForm, UserForm
from .utils import (
    ItemCollectionMeta, ItemMeta, default_admin_item_view, default_admin_list_view,
)


@admin_bp.before_request
@login_required
def before_request() -> Optional[Response]:
    if not current_user.admin:
        abort(403)


@admin_bp.route('/home')
def home() -> Response:
    return render_template('admin/index.html')


@admin_bp.route('/users/list')
def user_list() -> Response:
    return default_admin_list_view(
        ItemCollectionMeta(dataobject=user, order=[Sort(field='name')])
    )


@admin_bp.route('/users/<int:user_pk>', methods=['POST', 'GET'])
def user_detail(user_pk: int) -> Response:
    return default_admin_item_view(
        ItemMeta(
            dataobject=user, form=UserForm,
            message='dane użytkownika {obj_name} zostały zmienione',
            title_field='name', success_url='admin.user_list',
        ),
        user_pk,
    )


@admin_bp.route('/category/list')
def category_list() -> Response:
    return default_admin_list_view(
        ItemCollectionMeta(
            dataobject=category,  order=[Sort(field='menu_order'), Sort(field='title')]
        )
    )


@admin_bp.route('/category/<int:category_pk>', methods=['POST', 'GET'])
def category_detail(category_pk: int) -> Response:
    form_queries = {
        'parent': category.query(
            sort=[Sort(field='title')],
            filters=[Filter(field='pk', op='ne', value=category_pk)],
        )
    }
    return default_admin_item_view(
        ItemMeta(
            dataobject=category, form=CategoryForm,
            message='dane kategorii {obj_name} zostały zmienione', title_field='title',
            success_url='admin.category_list', form_queries=form_queries,
        ),
        category_pk,
    )


@admin_bp.route('/page/list')
def page_list() -> Response:
    return default_admin_list_view(
        ItemCollectionMeta(dataobject=page, order=[Sort(field='title')])
    )


@admin_bp.route('/page/<int:page_pk>', methods=['POST', 'GET'])
def page_detail(page_pk: int) -> Response:
    return default_admin_item_view(
        ItemMeta(
            dataobject=page, form=PageForm,
            message='dane strony {obj_name} zostały zmienione',
            title_field='title', success_url='admin.page_list',
        ),
        page_pk,
    )
