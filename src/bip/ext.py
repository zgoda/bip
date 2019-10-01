from flask_babel import Babel
from flask_bootstrap import Bootstrap
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy
from flask_wtf.csrf import CSRFProtect

from .utils.db import Model

db = SQLAlchemy(model_class=Model)
babel = Babel(default_locale='pl', default_timezone='Europe/Warsaw')
login_manager = LoginManager()
csrf = CSRFProtect()
bootstrap = Bootstrap()
