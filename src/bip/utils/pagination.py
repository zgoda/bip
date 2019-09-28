from flask import request, url_for, current_app


def url_for_other_page(page):
    args = request.view_args.copy()
    args['p'] = page
    return url_for(request.endpoint, **args)


def get_page(arg_name='p'):
    try:
        return int(request.args.get(arg_name, '1'))
    except ValueError:
        return 1


def paginate(query, page=None, size=None):
    if page is None:
        page = get_page()
    if size is None:
        size = current_app.config.get('LIST_SIZE', 20)
    return query.paginate(page, size)
