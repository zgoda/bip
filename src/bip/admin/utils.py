from collections import namedtuple
from typing import Any

from flask import Response, flash, redirect, render_template, request, url_for

ItemMeta = namedtuple(
    'ItemMeta',
    'dataobject,form,message,title_field,success_url,success_url_kwargs,template',
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
            return redirect(
                url_for(item_meta.success_url, **item_meta.success_url_kwargs)
            )
    context = {
        'object': obj,
        'form': form or item_meta.form(obj=obj)
    }
    return render_template(item_meta.template, **context)
