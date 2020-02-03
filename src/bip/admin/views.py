from typing import Optional

from flask import Response, abort, render_template
from flask_login import current_user, login_required

from ..models import Label, Page, User
from . import admin_bp
from .forms import LabelForm, PageForm, UserForm
from .utils import (
    ItemCollectionMeta, ItemMeta, default_admin_item_view, default_admin_list_view,
)

page_item_meta = ItemMeta(
    dataobject=Page, form=PageForm,
    message='dane strony {obj_name} zostały zmienione', success_url='admin.page_list',
    title_field='title',
)

user_item_meta = ItemMeta(
    dataobject=User, form=UserForm,
    message='dane użytkownika {obj_name} zostały zmienione',
    success_url='admin.user_list', title_field='name',
)

label_item_meta = ItemMeta(
    dataobject=Label, form=LabelForm,
    message='dane etykiety {obj_name} zostały zmienione',
    success_url='admin.label_list', title_field='name',
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
        ItemCollectionMeta(
            dataobject=User, order=[User.name], form=UserForm,
            message='now konto zostało utworzone',
        )
    )


@admin_bp.route('/users/<int:user_pk>', methods=['POST', 'GET'])
def user_detail(user_pk: int) -> Response:
    return default_admin_item_view(user_item_meta, user_pk)


@admin_bp.route('/page/list', methods=['POST', 'GET'])
def page_list() -> Response:
    return default_admin_list_view(
        ItemCollectionMeta(
            dataobject=Page, order=[Page.title], form=PageForm,
            message='nowa strona została utworzona',
        )
    )


@admin_bp.route('/page/<int:page_pk>', methods=['POST', 'GET'])
def page_detail(page_pk: int) -> Response:
    return default_admin_item_view(page_item_meta, page_pk)


@admin_bp.route('/label/list', methods=['POST', 'GET'])
def label_list() -> Response:
    return default_admin_list_view(
        ItemCollectionMeta(
            dataobject=Label, order=[Label.name], form=LabelForm,
            message='nowa etykieta została utworzona',
        )
    )


@admin_bp.route('/label/<int:label_pk>', methods=['POST', 'GET'])
def label_detail(label_pk: int) -> Response:
    return default_admin_item_view(label_item_meta, label_pk)
