import logging
import logging.config
import os
import tempfile
from typing import Any, Optional, Tuple

import keyring
import sentry_sdk
from flask import Response, render_template, request, send_from_directory
from keyrings.cryptfile.cryptfile import CryptFileKeyring
from sentry_sdk.integrations.flask import FlaskIntegration
from werkzeug.utils import ImportStringError

from ._version import get_version
from .admin import admin_bp
from .auth import auth_bp
from .ext import babel, bootstrap, csrf, login_manager
from .main import main_bp
from .models import User, db, get_db_driver
from .user import user_bp
from .utils.app import Application, is_test_env
from .utils.site import Site, test_site
from .utils.templates import extra_context, extra_filters


def make_app() -> Application:
    """Application object factory.

    :return: application object
    :rtype: Application
    """
    extra = {}
    instance_path = os.environ.get('INSTANCE_PATH')
    if instance_path:
        extra['instance_path'] = instance_path
    app = Application(__name__.split('.')[0], **extra)
    app.testing = is_test_env()
    configure_app(app)
    prepare_app(app)
    # setup keyring for headless environments
    if app.testing or not app.debug:
        keyring.set_keyring(CryptFileKeyring())
    # configure general logging
    if not app.debug:
        sentry_dsn = os.getenv('SENTRY_DSN')
        if sentry_dsn:
            version = get_version()
            sentry_sdk.init(
                dsn=sentry_dsn, release=f'bip@{version}',
                integrations=[FlaskIntegration()],
            )
        configure_logging()
    with app.app_context():
        configure_logging_handler(app)
        configure_database(app)
        configure_extensions(app)
        configure_templating(app)
        configure_hooks(app)
        configure_blueprints(app)
        configure_error_handlers(app)
    return app


def configure_app(app: Application) -> None:
    """Load application configuration.

    :param app: application object
    :type app: Application
    :param env: environment name (may be None)
    :type env: Optional[str]
    """
    app.config.from_object('bip.config')
    if app.testing:
        try:
            app.config.from_object('bip.config_test')
        except ImportStringError:
            app.logger.info('no environment config for testing')

    @app.route('/attachment/<filename>', endpoint='attachment')
    def serve_attachment(filename: str) -> Response:
        kw = {
            'as_attachment': True,
        }
        attachment_filename = request.args.get('save')
        if attachment_filename:
            kw['attachment_filename'] = attachment_filename  # type: ignore
        dir_name = os.path.join(app.instance_path, app.config['ATTACHMENTS_DIR'])
        return send_from_directory(dir_name, filename, **kw)


def configure_logging_handler(app: Application) -> None:
    """Bind application logging to Gunicorn handler.

    This is done only in production and only if Gunicorn logger has any
    handlers defined.

    :param app: application object
    :type app: Application
    """
    if app.debug:
        return
    gunicorn_logger = logging.getLogger('gunicorn.error')
    if gunicorn_logger.handlers:
        app.logger.handlers = gunicorn_logger.handlers
        app.logger.setLevel(gunicorn_logger.level)


def configure_database(app: Application) -> None:
    """Configure application database connectivity.

    :param app: application object
    :type app: Application
    """
    driver = get_db_driver()
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


def prepare_app(app: Application) -> None:
    """Former ``before_first_request`` hook, now standalone function.

    :param app: application object
    :type app: Application
    """
    if app.debug and not os.getenv('SITE_JSON'):
        site = test_site()
    else:
        site_object_path = os.path.abspath(os.environ['SITE_JSON'])
        with open(site_object_path, 'r') as fp:
            site = Site.from_json(fp.read())
    app.site = app.jinja_env.globals['site'] = site  # type: ignore


def configure_hooks(app: Application) -> None:
    """Set up application lifetime hooks.

    :param app: application object
    :type app: Application
    """

    @app.before_request
    def db_connect() -> None:
        db.connect(reuse_if_open=True)

    @app.teardown_request
    def db_close(exc: Any) -> None:
        if not db.is_closed():
            db.close()


def configure_blueprints(app: Application) -> None:
    """Register (mount) blueprint objects.

    :param app: application object
    :type app: Application
    """
    app.register_blueprint(main_bp)
    app.register_blueprint(admin_bp, url_prefix='/admin')
    app.register_blueprint(auth_bp, url_prefix='/identyfikacja')
    app.register_blueprint(user_bp, url_prefix='/uzytkownik')


def configure_extensions(app: Application) -> None:
    """Register and configure framework extensions.

    :param app: application object
    :type app: Application
    """
    babel.init_app(app, default_locale='pl', default_timezone='Europe/Warsaw')
    csrf.init_app(app)
    bootstrap.init_app(app)

    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'  # type: ignore
    login_manager.login_message_category = 'warning'
    login_manager.login_message = 'Musisz się zalogować by uzyskać dostęp do tej strony'

    @login_manager.user_loader
    def get_user(userid: str) -> Optional[User]:  # pylint: disable=unused-variable
        return User.get_or_none(User.pk == userid)


def configure_templating(app: Application) -> None:
    """Configure template system extensions.

    :param app: application object
    :type app: Application
    """
    app.jinja_env.globals.update(extra_context())
    app.jinja_env.filters.update(extra_filters())


def configure_error_handlers(app: Application) -> None:
    """Configure global error handlers.

    :param app: application object
    :type app: Application
    """

    @app.errorhandler(403)
    def forbidden_page(_error: Any) -> Tuple[str, int]:
        return render_template('errors/403.html'), 403

    @app.errorhandler(404)
    def page_not_found(_error: Any) -> Tuple[str, int]:
        return render_template('errors/404.html'), 404

    @app.errorhandler(500)
    def server_error_page(_error: Any) -> Tuple[str, int]:
        return render_template('errors/500.html'), 500


def configure_logging() -> None:
    """Configure application logging on prod.

    This configuration is overwritten if running under Gunicorn.
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
