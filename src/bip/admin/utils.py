from collections import namedtuple
from typing import Any

from flask import Response, flash, redirect, render_template, request, url_for

from ..utils.pagination import paginate

ItemMeta = namedtuple(
    'ItemMeta',
    'dataobject,form,message,title_field,success_url,template,success_url_kwargs',
    defaults=(None, None)
)

ItemCollectionMeta = namedtuple(
    'ItemCollectionMeta', 'dataobject,template,orders,filters',
    defaults=(None, None, None),
)


def default_admin_item_view(item_meta: ItemMeta, item_pk: Any) -> Response:
    obj = item_meta.dataobject.get(item_pk, abort_on_none=True)
    form = None
    if request.method == 'POST':
        form = item_meta.form()
        if form.validate_on_submit():
            obj = form.save(obj)
            flash(
                item_meta.message.format(
                    obj_name=getattr(obj, item_meta.title_field)
                ), category='success',
            )
            url_kwargs = item_meta.success_url_kwargs
            if url_kwargs is None:
                url_kwargs = {}
            return redirect(url_for(item_meta.success_url, **url_kwargs))
    context = {
        'object': obj,
        'form': form or item_meta.form(obj=obj)
    }
    template = item_meta.template
    if template is None:
        template = f'admin/{item_meta.dataobject.object_name}_detail.html'
    return render_template(template, **context)


def default_admin_list_view(item_meta: ItemCollectionMeta) -> Response:
    query = item_meta.dataobject.query(sort=item_meta.orders, filters=item_meta.filters)
    context = {
        'pagination': paginate(query)
    }
    template = item_meta.template
    if template is None:
        template = f'admin/{item_meta.dataobject.object_name}_list.html'
    return render_template(template, **context)
