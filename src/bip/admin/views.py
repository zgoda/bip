from flask import abort, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required

from ..data import Sort, category, page, user
from ..utils.pagination import paginate
from . import admin_bp
from .forms import CategoryForm, PageForm, UserForm


@admin_bp.before_request
@login_required
def before_request():
    if not current_user.admin:
        abort(403)


@admin_bp.route('/home')
def home():
    return render_template('admin/index.html')


@admin_bp.route('/users/list')
def user_list():
    query = user.query(sort=[Sort(field='name')])
    context = {
        'pagination': paginate(query)
    }
    return render_template('admin/user_list.html', **context)


@admin_bp.route('/users/<int:user_pk>', methods=['POST', 'GET'])
def user_detail(user_pk):
    user_obj = user.get(user_pk, abort_on_none=True)
    form = None
    if request.method == 'POST':
        form = UserForm()
        if form.validate_on_submit():
            user_obj = form.save(obj=user_obj)
            flash(
                f'dane użytkownika {user_obj.name} zostały zmienione',
                category='success',
            )
            return redirect(url_for('admin.user_list'))
    context = {
        'user': user_obj,
        'form': form or UserForm(obj=user_obj),
    }
    return render_template('admin/user_detail.html', **context)


@admin_bp.route('/category/list')
def category_list():
    query = category.query(sort=[Sort(field='menu_order'), Sort(field='title')])
    context = {
        'pagination': paginate(query)
    }
    return render_template('admin/category_list.html', **context)


@admin_bp.route('/category/<int:category_pk>', methods=['POST', 'GET'])
def category_detail(category_pk):
    category_obj = category.get(category_pk, abort_on_none=True)
    form = None
    if request.method == 'POST':
        form = CategoryForm()
        if form.validate_on_submit():
            category_obj = form.save(category_obj)
            flash(
                f'dane kategorii {category_obj.title} zostały zmienione',
                category='success',
            )
            return redirect(url_for('admin.category_list'))
    context = {
        'category': category_obj,
        'form': form or CategoryForm(obj=category_obj)
    }
    return render_template('admin/category_detail.html', **context)


@admin_bp.route('/page/list')
def page_list():
    query = page.query(sort=[Sort(field='title')])
    context = {
        'pagination': paginate(query)
    }
    return render_template('admin/page_list.html', **context)


@admin_bp.route('/page/<int:page_pk>', methods=['POST', 'GET'])
def page_detail(page_pk):
    page_obj = page.get(page_pk, abort_on_none=True)
    form = None
    if request.method == 'POST':
        form = PageForm()
        if form.validate_on_submit():
            page_obj = form.save(page_obj)
            flash(f'dane strony {page_obj.title} zostały zmienione', category='success')
            return redirect(url_for('admin.page_list'))
    context = {
        'page': page_obj,
        'form': form or PageForm(obj=page_obj)
    }
    return render_template('admin/page_detail.html', **context)
