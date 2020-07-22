import logging
import os
import tempfile
from typing import Optional

import keyring
import sentry_sdk
from flask import render_template, send_from_directory
from keyrings.cryptfile.cryptfile import CryptFileKeyring
from sentry_sdk.integrations.flask import FlaskIntegration
from werkzeug.utils import ImportStringError

from .__version__ import get_version
from .admin import admin_bp
from .auth import auth_bp
from .ext import babel, bootstrap, csrf, login_manager
from .main import main_bp
from .models import User, db
from .user import user_bp
from .utils.app import Application
from .utils.site import Site, test_site
from .utils.templates import extra_context, extra_filters


def make_app(env: Optional[str] = None) -> Application:
    """Application object factory.

    :param env: environment name, defaults to None
    :type env: Optional[str], optional
    :return: application object
    :rtype: Application
    """
    flask_environment = os.environ.get('FLASK_ENV', '')
    if flask_environment == 'production':
        sentry_dsn = os.getenv('SENTRY_DSN')
        if sentry_dsn:
            version = get_version()
            sentry_sdk.init(
                dsn=sentry_dsn, release=f'bip@{version}',
                integrations=[FlaskIntegration()],
            )
        else:
            configure_logging()
    extra = {}
    instance_path = os.environ.get('INSTANCE_PATH')
    if instance_path:
        extra['instance_path'] = instance_path
    app = Application(__name__.split('.')[0], **extra)
    configure_app(app, env)
    # setup keyring for headless environments
    if flask_environment == 'production' or app.testing:
        keyring.set_keyring(CryptFileKeyring())
    with app.app_context():
        configure_logging_handler(app)
        configure_database(app)
        configure_extensions(app)
        configure_templating(app)
        configure_hooks(app)
        configure_blueprints(app)
        configure_error_handlers(app)
    return app


def configure_app(app: Application, env: Optional[str]):
    """Load application configuration.

    :param app: application object
    :type app: Application
    :param env: environment name (may be None)
    :type env: Optional[str]
    """
    app.config.from_object('bip.config')
    if env is not None:
        try:
            app.config.from_object(f'bip.config_{env}')
        except ImportStringError:
            app.logger.info(f'no environment config for {env}')

    @app.route('/attachment/<filename>', endpoint='attachment')
    def serve_attachment(filename):
        dir_name = os.path.join(app.instance_path, app.config['ATTACHMENTS_DIR'])
        return send_from_directory(dir_name, filename, as_attachment=True)


def configure_logging_handler(app: Application):
    """Bind application logging to Gunicorn handler. This is done only in
    production and only if Gunicorn logger has any handlers defined.

    :param app: application object
    :type app: Application
    """
    if app.debug or app.testing:
        return
    gunicorn_logger = logging.getLogger('gunicorn.error')
    if gunicorn_logger.handlers:
        app.logger.handlers = gunicorn_logger.handlers
        app.logger.setLevel(gunicorn_logger.level)


def configure_database(app: Application):
    """Configure application database connectivity.

    :param app: application object
    :type app: Application
    """
    driver = os.getenv('DB_DRIVER', 'sqlite')
    if app.testing:
        tmp_dir = tempfile.mkdtemp()
        db_name = os.path.join(tmp_dir, 'bip.db')
    else:
        db_name = os.getenv('DB_NAME')
    if driver == 'sqlite':
        kw = {
            'pragmas': {
                'journal_mode': 'wal',
                'cache_size': -1 * 64000,
                'foreign_keys': 1,
                'ignore_check_constraints': 0,
                'synchronous': 0,
            }
        }
        if db_name is None:
            db_name = ':memory:'
            kw = {}
    else:
        kw = {
            'host': os.getenv('DB_HOST'),
            'port': os.getenv('DB_PORT'),
            'user': os.getenv('DB_USER'),
            'password': os.getenv('DB_PASSWORD')
        }
    db.init(db_name, **kw)


def configure_hooks(app: Application):
    """Setup application lifetime hooks.

    :param app: application object
    :type app: Application
    """

    @app.before_first_request
    def load_site_objects():
        if app.testing and not os.getenv('SITE_JSON'):
            site = test_site()
        else:
            site_object_path = os.path.abspath(os.environ['SITE_JSON'])
            with open(site_object_path) as fp:
                site = Site.from_json(fp.read())
        app.site = app.jinja_env.globals['site'] = site

    @app.before_request
    def db_connect():
        db.connect(reuse_if_open=True)

    @app.teardown_request
    def db_close(exc):
        if not db.is_closed():
            db.close()


def configure_blueprints(app: Application):
    """Register (mount) blueprint objects.

    :param app: application object
    :type app: Application
    """
    app.register_blueprint(main_bp)
    app.register_blueprint(admin_bp, url_prefix='/admin')
    app.register_blueprint(auth_bp, url_prefix='/identyfikacja')
    app.register_blueprint(user_bp, url_prefix='/uzytkownik')


def configure_extensions(app: Application):
    """Register and configure framework extensions.

    :param app: application object
    :type app: Application
    """
    babel.init_app(app)
    csrf.init_app(app)
    bootstrap.init_app(app)

    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    login_manager.login_message_category = 'warning'
    login_manager.login_message = 'Musisz się zalogować by uzyskać dostęp do tej strony'

    @login_manager.user_loader
    def get_user(userid: str) -> Optional[User]:  # pylint: disable=unused-variable
        return User.get_or_none(User.pk == userid)


def configure_templating(app: Application):
    """Configure template system extensions.

    :param app: application object
    :type app: Application
    """
    app.jinja_env.globals.update(extra_context())
    app.jinja_env.filters.update(extra_filters())


def configure_error_handlers(app: Application):
    """Configure global error handlers.

    :param app: application object
    :type app: Application
    """

    @app.errorhandler(403)
    def forbidden_page(error):  # pylint: disable=unused-variable
        return render_template('errors/403.html'), 403

    @app.errorhandler(404)
    def page_not_found(error):  # pylint: disable=unused-variable
        return render_template('errors/404.html'), 404

    @app.errorhandler(500)
    def server_error_page(error):  # pylint: disable=unused-variable
        return render_template('errors/500.html'), 500


def configure_logging():
    """Configure application logging on prod. This configuration is
    overwritten if running under Gunicorn.
    """
    logging.config.dictConfig({
        'version': 1,
        'formatters': {
            'default': {
                'format': '[%(asctime)s] %(levelname)s in %(module)s: %(message)s'
            }
        },
        'handlers': {
            'wsgi': {
                'class': 'logging.StreamHandler',
                'stream': 'ext://flask.logging.wsgi_errors_stream',
                'formatter': 'default',
            }
        },
        'root': {
            'level': 'INFO',
            'handlers': ['wsgi'],
        },
    })
