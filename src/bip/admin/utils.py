from dataclasses import dataclass, field
from typing import Any, Mapping, Optional, Sequence, Type, Union

from flask import Response, flash, redirect, render_template, request, url_for
from flask_wtf import FlaskForm
from peewee import Expression, Field, Model

from ..utils.http import or_404
from ..utils.pagination import paginate


@dataclass
class ItemMeta:
    dataobject: Model
    form: Type[FlaskForm]
    message: str
    success_url: str
    title_field: Optional[str] = None
    template: Optional[str] = None
    success_url_kwargs: Mapping[str, Any] = field(default_factory=dict)


@dataclass
class ItemCollectionMeta:
    dataobject: Model
    form: Optional[Type[FlaskForm]]
    message: Optional[str] = None
    template: Optional[str] = None
    order: Optional[Field] = None
    filters: Optional[Sequence[Expression]] = None


def default_admin_item_view(item_meta: ItemMeta, item_pk: Any) -> Union[str, Response]:
    """Default item view for admin interface.

    :param item_meta: item metadata object
    :type item_meta: ItemMeta
    :param item_pk: item lookup key
    :type item_pk: Any
    :return: Flask response (Response object or str)
    :rtype: Union[str, Response]
    """
    obj = or_404(item_meta.dataobject.get(item_pk))
    form = None
    if request.method == 'POST':
        form = item_meta.form()
        if form.validate_on_submit():
            obj = form.save(obj)
            message = item_meta.message.format(
                obj_name=getattr(obj, item_meta.title_field)  # skipcq: PTC-W0034
            )
            flash(message, category='success')
            return redirect(
                url_for(item_meta.success_url, **item_meta.success_url_kwargs)
            )
    form = form or item_meta.form(obj=obj)
    context = {
        'object': obj,
        'form': form,
    }
    template = f'admin/{item_meta.dataobject._meta.name}_detail.html'
    return render_template(template, **context)


def default_admin_list_view(item_meta: ItemCollectionMeta) -> Union[str, Response]:
    """Default collection (list) view for admin interface.

    :param item_meta: item collection metadata object
    :type item_meta: ItemCollectionMeta
    :return: Flask response (Response object or str)
    :rtype: Union[str, Response]
    """
    form = None
    if item_meta.form:
        form = item_meta.form()
        if form.validate_on_submit():
            form.save()
            flash(item_meta.message, category='success')
            return redirect(request.path)
    query = item_meta.dataobject.select()
    query = query.order_by(item_meta.order)
    context = {
        'pagination': paginate(query),
        'form': form,
    }
    template = f'admin/{item_meta.dataobject.__name__.lower()}_list.html'
    return render_template(template, **context)
