from flask_babel import Babel
from flask_bootstrap import Bootstrap
from flask_login import LoginManager
from flask_wtf.csrf import CSRFProtect

babel = Babel(default_locale='pl', default_timezone='Europe/Warsaw')
login_manager = LoginManager()
csrf = CSRFProtect()
bootstrap = Bootstrap()
