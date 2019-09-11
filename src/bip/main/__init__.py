from flask import Blueprint

main_bp = Blueprint('main', __name__, template_folder='templates')

from . import views  # noqa: F401,E402
