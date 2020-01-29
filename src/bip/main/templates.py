from . import main_bp
from .utils import editor_tools, admin_tools


@main_bp.app_context_processor
def extra_context():
    return {
        'editortools': editor_tools(),
        'admintools': admin_tools(),
    }
