from flask import abort, render_template
from flask_login import current_user, login_required

from ..data import Sort, category, page, user
from . import admin_bp
from .forms import CategoryForm, PageForm, UserForm
from .utils import (
    ItemCollectionMeta, ItemMeta, default_admin_item_view, default_admin_list_view,
)


@admin_bp.before_request
@login_required
def before_request():
    if not current_user.admin:
        abort(403)


category_item_meta = ItemMeta(
    dataobject=category, form=CategoryForm,
    message='dane kategorii {obj_name} zostały zmienione', title_field='title',
    success_url='admin.category_list'
)

category_list_meta = ItemCollectionMeta(
    dataobject=category, template='admin/category_list.html',
    orders=[Sort(field='menu_order'), Sort(field='title')],
)

user_item_meta = ItemMeta(
    dataobject=user, form=UserForm,
    message='dane użytkownika {obj_name} zostały zmienione', title_field='name',
    success_url='admin.user_list'
)

user_list_meta = ItemCollectionMeta(
    dataobject=user, template='admin/user_list.html', orders=[Sort(field='name')]
)

page_item_meta = ItemMeta(
    dataobject=page, form=PageForm, message='dane strony {obj_name} zostały zmienione',
    title_field='title', success_url='admin.page_list'
)

page_list_meta = ItemCollectionMeta(
    dataobject=page, template='admin/page_list.html', orders=[Sort(field='title')]
)


@admin_bp.route('/home')
def home():
    return render_template('admin/index.html')


@admin_bp.route('/users/list')
def user_list():
    return default_admin_list_view(user_list_meta)


@admin_bp.route('/users/<int:user_pk>', methods=['POST', 'GET'])
def user_detail(user_pk):
    return default_admin_item_view(user_item_meta, user_pk)


@admin_bp.route('/category/list')
def category_list():
    return default_admin_list_view(category_list_meta)


@admin_bp.route('/category/<int:category_pk>', methods=['POST', 'GET'])
def category_detail(category_pk):
    return default_admin_item_view(category_item_meta, category_pk)


@admin_bp.route('/page/list')
def page_list():
    return default_admin_list_view(page_list_meta)


@admin_bp.route('/page/<int:page_pk>', methods=['POST', 'GET'])
def page_detail(page_pk):
    return default_admin_item_view(page_item_meta, page_pk)
