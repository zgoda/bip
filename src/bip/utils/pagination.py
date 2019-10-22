from typing import Optional, Union

from flask import current_app, request, url_for
from flask_sqlalchemy import BaseQuery, Pagination


def url_for_other_page(page: Union[int, str]) -> str:
    args = request.view_args.copy()
    args['p'] = page
    return url_for(request.endpoint, **args)


def get_page(arg_name='p') -> int:
    try:
        return int(request.args.get(arg_name, '1'))
    except ValueError:
        return 1


def paginate(
            query: BaseQuery, page: Optional[int] = None, size: Optional[int] = None
        ) -> Pagination:
    if page is None:
        page = get_page()
    if size is None:
        size = current_app.config.get('LIST_SIZE', 20)
    return query.paginate(page, size)
