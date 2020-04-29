from . import main_bp
from .utils import admin_tools, editor_tools, labels, page_links


@main_bp.app_context_processor
def extra_context() -> dict:
    """Things to be added to Jinja context.

    :return: extra context items
    :rtype: dict
    """
    return {
        'editortools': editor_tools(),
        'admintools': admin_tools(),
        'pages': page_links(),
        'labels': labels(),
    }
