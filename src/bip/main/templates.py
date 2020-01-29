from . import main_bp
from .utils import admin_tools, editor_tools, page_links


@main_bp.app_context_processor
def extra_context():
    return {
        'editortools': editor_tools(),
        'admintools': admin_tools(),
        'pages': page_links(),
    }
