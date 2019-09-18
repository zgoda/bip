from . import main_bp
from .utils import menu_items


@main_bp.app_context_processor
def extra_context():
    return {
        'menu': menu_items(),
    }
