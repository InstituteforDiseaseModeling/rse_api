import importlib
import os
from flask import Flask
from flask.cli import AppGroup

from rse_api.cli import add_cli
from rse_api.decorators import singleton_function
from rse_api.errors import register_common_error_handlers

HAS_DRAMATIQ=importlib.find_loader('dramatiq') is not None
HAS_RABBIT=importlib.find_loader('pika') is not None

__author__ = """Clinton Collins"""
__email__ = 'ccollins@idmod.org'
__version__ = '1.0.0'

@singleton_function
def get_application(setting_object_path: str=None, setting_environment_variable: str=None, strict_slashes: bool=False,
                    default_error_handlers: bool=True) -> Flask:
    """
    Returns a Flask Application object. This function is a singleton function

    :param default_error_handlers: Should the default error handlers for SQlAlchemy and Marshmallow be added?
    :param setting_object_path: Optional Python import path to the default settings objects
    :param setting_environment_variable: Optional environment variable that stores path to setting files
    :param strict_slashes: Should we use strict slashes(Ie a call to /projects will fail but a call to /projects will
      succeed
    :return: Flask app
    """
    app = Flask(__name__)
    if setting_object_path:
        app.logger.debug('Loading Application settings from {}'.format(setting_object_path))
        app.config.from_object(setting_object_path)
    if setting_environment_variable:
        app.logger.debug('Loading Application settings from the file {}'.format(os.environ[setting_environment_variable]))
        app.config.from_envvar(setting_environment_variable)
    app.url_map.strict_slashes = strict_slashes
    add_cli(app)

    if default_error_handlers:
        register_common_error_handlers(app)

    if HAS_DRAMATIQ and HAS_RABBIT:
        rabbit_url =app.config.get('RABBIT_URL', None)
        if rabbit_url:
            from dramatiq.brokers.rabbitmq import URLRabbitmqBroker
            import dramatiq
            broker = URLRabbitmqBroker(rabbit_url)
            dramatiq.set_broker(broker)
    return app


@singleton_function
def get_worker_cli(app, load_workers_func=None):
    # Get flask db should have been called before this with any setup needed
    worker_cli = AppGroup('workers', help="Commands related to workers")

    if HAS_DRAMATIQ:
        import dramatiq

        workers = dramatiq.get_broker().get_declared_actors()
        if len(workers) > 0:
            @worker_cli.command('start', help="Starts all the workers")
            def start_workers():
                if callable(load_workers_func):
                    load_workers_func()
                dramatiq.get_broker().get_declared_actors()

        app.cli.add_command(worker_cli)

    return worker_cli