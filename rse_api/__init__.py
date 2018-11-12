import logging
import os
import signal
import sys
from importlib import util
from typing import Callable

from flask import Flask
from flask.cli import AppGroup

from rse_api.cli import add_cli
from rse_api.decorators import singleton_function, CRON_JOBS
from rse_api.errors import register_common_error_handlers


HAS_DRAMATIQ = util.find_spec('dramatiq') is not None
HAS_RABBIT = util.find_spec('pika') is not None
HAS_REDIS = util.find_spec('redis') is not None
HAS_APSCHEDULER = util.find_spec('apscheduler') is not None

__author__ = """Clinton Collins"""
__email__ = 'ccollins@idmod.org'
__version__ = '1.0.0'


@singleton_function
def default_dramatiq_setup_broker(app):
    if HAS_DRAMATIQ and (HAS_RABBIT or HAS_REDIS):
        import dramatiq
        import dramatiq.brokers
        from rse_api.tasks.app_context_middleware import AppContextMiddleware

        broker = None
        # if we are testing, setup stub broker
        if (app.config.get('TESTING', False) or app.config.get('FLASK_ENV', '') == 'development') and \
                not app.config.get('DRAMATIQ_USE_PROD', False):
            app.logger.info('Using Stub Broker')
            from dramatiq.brokers.stub import StubBroker
            broker = dramatiq.brokers.stub.StubBroker()
        else:
            if HAS_RABBIT:
                broker_url = app.config.get('RABBIT_URI', None)
                from dramatiq.brokers.rabbitmq import URLRabbitmqBroker
                app.logger.info('Connecting to Rabbit MQ @ {}'.format(broker_url))
                broker = URLRabbitmqBroker(broker_url)
            else:
                broker_url = app.config.get('REDIS_URI', None)
                from dramatiq.brokers.redis import URLRedisBroker
                app.logger.info('Connecting to Redis @ {}'.format(broker_url))
                broker = URLRedisBroker(broker_url)

        if broker is not None:
            dramatiq.set_broker(broker)
            broker.add_middleware(AppContextMiddleware(app))
        # add worker cli as well
        cli = get_worker_cli(app)
        return broker
    return None


@singleton_function
def get_application(setting_object_path: str=None, setting_environment_variable: str=None, strict_slashes: bool=False,
                    default_error_handlers: bool=True, setup_broker_func: Callable = default_dramatiq_setup_broker) -> Flask:
    """
    Returns a Flask Application object. This function is a singleton function

    :param setup_broker_func: Function callback to setup brokers for queues. By default a function that checks for dramatiq
    is called and if deted
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

    if callable(setup_broker_func):
        app.broker = setup_broker_func(app)

    return app


@singleton_function
def get_worker_cli(app,):
    # Get flask db should have been called before this with any setup needed
    worker_cli = AppGroup('workers', help="Commands related to workers")

    if HAS_DRAMATIQ:
        import dramatiq

        @worker_cli.command('start', help="Starts all the workers")
        def start_workers():
            from dramatiq import   __main__ as dm
            args = dm.parse_arguments()
            args.module = None
            args.modules = []
            args.workers = []
            dm.parse_arguments = lambda : args
            dm.import_broker = lambda x: ('rse_api', app.broker)
            dm.main()

        @worker_cli.command('list', help="Lists all the workers")
        def list_workers():
            workers = dramatiq.get_broker().get_declared_actors()
            workers = sorted(workers)
            print('Workers available: ')
            [print(worker) for worker in workers]

    if HAS_APSCHEDULER:
        from apscheduler.schedulers.blocking import BlockingScheduler

        @worker_cli.command('cron', help="Run any scheduled workers")
        def run_cron_workers():
            logging.basicConfig(
                format="[%(asctime)s] [PID %(process)d] [%(threadName)s] [%(name)s] [%(levelname)s] %(message)s",
                level=logging.DEBUG,
            )

            # Pika is a bit noisy w/ Debug logging so we have to up its level.
            logging.getLogger("pika").setLevel(logging.WARNING)
            scheduler = BlockingScheduler()
            for trigger, module_path, func_name in CRON_JOBS:
                job_path = f"{module_path}:{func_name}.send"
                job_name = f"{module_path}.{func_name}"
                scheduler.add_job(job_path, trigger=trigger, name=job_name)

            def shutdown(signum, frame):
                scheduler.shutdown()

            signal.signal(signal.SIGINT, shutdown)
            signal.signal(signal.SIGTERM, shutdown)

            scheduler.start()

    app.cli.add_command(worker_cli)

    return worker_cli
