from . import main_bp
from .utils import menu_items, menu_tools, admin_tools


@main_bp.app_context_processor
def extra_context() -> dict:
    return {
        'menu': menu_items(),
        'tools': menu_tools(),
        'admintools': admin_tools(),
    }
