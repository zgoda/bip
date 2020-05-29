import os
from typing import Optional, Union

from flask import (
    Response, abort, current_app, flash, redirect, render_template, request,
)
from flask_login import current_user, login_required
from werkzeug.exceptions import BadRequest

from ..models import Attachment, Label, Page, PageLabel, User, db
from ..utils.http import or_404
from . import admin_bp
from .forms import AttachmentCreateForm, LabelForm, PageForm, UserForm, AttachmentForm
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

attachment_item_meta = ItemMeta(
    dataobject=Attachment, form=AttachmentForm,
    message='dane załącznika {obj_name} zostały zmienione', title_field='title',
    success_url='admin.attachment_list',
)


@admin_bp.before_request
@login_required
def before_request() -> Optional[Response]:
    if not current_user.admin:
        abort(403)


@admin_bp.route('/home')
def home() -> str:
    return render_template('admin/index.html')


@admin_bp.route('/users/list')
def user_list() -> Union[Response, str]:
    return default_admin_list_view(
        ItemCollectionMeta(
            dataobject=User, order=[User.name], form=UserForm,
            message='now konto zostało utworzone',
        )
    )


@admin_bp.route('/users/<int:user_pk>', methods=['POST', 'GET'])
def user_detail(user_pk: int) -> Union[Response, str]:
    return default_admin_item_view(user_item_meta, user_pk)


@admin_bp.route('/page/list', methods=['POST', 'GET'])
def page_list() -> Union[Response, str]:
    return default_admin_list_view(
        ItemCollectionMeta(
            dataobject=Page, order=[Page.title], form=PageForm,
            message='nowa strona została utworzona',
        )
    )


@admin_bp.route('/page/<int:page_pk>', methods=['POST', 'GET'])
def page_detail(page_pk: int) -> Union[Response, str]:
    return default_admin_item_view(page_item_meta, page_pk)


@admin_bp.route('/page/<int:page_pk>/labels', methods=['POST', 'GET'])
def page_labels(page_pk: int) -> Union[Response, str]:
    page = or_404(Page.get_or_none(Page.pk == page_pk))
    if request.method == 'POST':
        label_ids = request.form.getlist('label')
        op = request.form.get('op')
        if op == 'add':
            with db.atomic():
                for label_pk in label_ids:
                    PageLabel.create(page=page, label=label_pk)
        elif op == 'remove':
            query = PageLabel.delete().where(PageLabel.pk.in_(label_ids))
            query.execute()
        else:
            raise BadRequest(f'unknown operation {op}')
        flash(f'etykiety strony {page.title} zostały zmienione', category='success')
        return redirect(request.path)
    cur_page_labels = page.labels(order=Label.name)
    page_label_ids = [pl.label.pk for pl in cur_page_labels]
    available_labels = (
        Label.select()
        .where(Label.pk.not_in(page_label_ids))
        .order_by(Label.name)
    )
    ctx = {
        'page': page,
        'page_labels': cur_page_labels,
        'available_labels': available_labels,
    }
    return render_template('admin/page_labels.html', **ctx)


@admin_bp.route('/page/<int:page_pk>/attachments', methods=['POST', 'GET'])
def page_attachments(page_pk: int) -> Union[Response, str]:
    page = or_404(Page.get_or_none(Page.pk == page_pk))
    form = AttachmentCreateForm()
    if request.method == 'POST':
        has_err = True
        op = request.form.get('op')
        if op == 'add':
            if form.validate_on_submit():
                has_err = False
                form.save(page)
        elif op == 'remove':
            attachment_ids = request.form.getlist('attachment')
            files_dir = os.path.join(
                current_app.instance_path, current_app.config['ATTACHMENTS_DIR']
            )
            query = Attachment.select().where(Attachment.pk.in_(attachment_ids))
            with db.atomic():
                for att in query:
                    path = os.path.join(files_dir, att.filename)
                    att.delete_instance()
                    os.remove(path)
                has_err = False
        else:
            raise BadRequest(f'unknown operation {op}')
        if not has_err:
            flash(
                f'załączniki strony {page.title} zostały zaktualizowane',
                category='success',
            )
            return redirect(request.path)
    ctx = {
        'page': page,
        'form': form,
    }
    return render_template('admin/page_attachments.html', **ctx)


@admin_bp.route('/label/list', methods=['POST', 'GET'])
def label_list() -> Union[Response, str]:
    return default_admin_list_view(
        ItemCollectionMeta(
            dataobject=Label, order=[Label.name], form=LabelForm,
            message='nowa etykieta została utworzona',
        )
    )


@admin_bp.route('/label/<int:label_pk>', methods=['POST', 'GET'])
def label_detail(label_pk: int) -> Union[Response, str]:
    return default_admin_item_view(label_item_meta, label_pk)


@admin_bp.route('/attachment/list')
def attachment_list() -> Union[Response, str]:
    return default_admin_list_view(
        ItemCollectionMeta(
            dataobject=Attachment, order=[Attachment.title], form=None
        )
    )


@admin_bp.route('/attachment/<int:attachment_pk>', methods=['POST', 'GET'])
def attachment_detail(attachment_pk: int) -> Union[Response, str]:
    return default_admin_item_view(attachment_item_meta, attachment_pk)
