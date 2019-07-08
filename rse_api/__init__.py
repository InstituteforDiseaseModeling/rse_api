from __future__ import annotations
import logging
import os
import signal
from importlib import util
from typing import Callable, Optional
import click
from flask import Flask
from flask.cli import AppGroup
from rse_api.cli import add_cli
from rse_api.decorators import singleton_function
from rse_api.errors import register_common_error_handlers

HAS_DRAMATIQ = util.find_spec('dramatiq') is not None
HAS_RESTFUL = util.find_spec('flask_restful') is not None
HAS_RABBIT = util.find_spec('pika') is not None
HAS_REDIS = util.find_spec('redis') is not None
HAS_APSCHEDULER = util.find_spec('apscheduler') is not None

__author__ = """Clinton Collins"""
__email__ = 'ccollins@idmod.org'
__version__ = '1.0.6'


@singleton_function
def default_dramatiq_setup_result_backend(app: Flask, broker: 'dramatiq.broker.Broker') -> \
        'dramatiq.results.backends.RedisBackend':
    """
    The default command used for setting up a Result Backend. By default we use Redis as our Result Backend.
    The connection string for Redis is from the Flask Config Key REDIS_URI

    If either Dramatiq or Redis packages are missing from the environment, this will return None

    We will also set the
    Args:
        app: Flask app that this broker is part of
        broker: Broker to attach the result backend to

    Returns:
        A Result backend

    See Also:
        - https://dramatiq.io/advanced.html?highlight=results#message-results
    """
    result_backend = None
    if HAS_DRAMATIQ and HAS_REDIS:
        from dramatiq.results import Results
        from dramatiq.results.backends import RedisBackend
        backend_url = app.config.get('REDIS_URI', None)
        result_backend = Results(backend=RedisBackend(url=backend_url))
        broker.add_middleware(result_backend)
    return result_backend


@singleton_function
def default_dramatiq_setup_broker(app: Flask) -> 'dramatiq.broker.Broker':
    """
    The default broker setup function. For the


    If either Dramatiq or Pika(RabbitMq Client) packages are missing from the environment, this will return None

    Args:
        app:

    Returns:

    """
    # If we are generation documentation, don't try to setup dramatiq
    if HAS_DRAMATIQ and (HAS_RABBIT or HAS_REDIS):
        import dramatiq
        import dramatiq.brokers
        from rse_api.tasks.app_context_middleware import AppContextMiddleware

        broker = None
        # if we are testing, setup stub broker
        if (app.config.get('TESTING', False) or app.env in ['development', 'testing', 'documentation']) and \
                not app.config.get('DRAMATIQ_USE_PROD', False):
            app.logger.info('Using Stub Broker')
            if os.name == 'nt':
                # at moment, windows cannot use stub broker
                if not HAS_RABBIT:
                    raise NotImplementedError("Windows does not support StubBroker. Please use RabbitMQ")

                broker_url = app.config.get('RABBIT_URI', None)
                from dramatiq.brokers.rabbitmq import URLRabbitmqBroker
                app.logger.info('Connecting to Rabbit MQ @ {}'.format(broker_url))
                broker = URLRabbitmqBroker(broker_url)
            else:
                from dramatiq.brokers.stub import StubBroker
                broker = StubBroker()
        else:
            if HAS_RABBIT:
                broker_url = app.config.get('RABBIT_URI', None)

                from dramatiq.brokers.rabbitmq import URLRabbitmqBroker
                app.logger.info('Connecting to Rabbit MQ @ {}'.format(broker_url))
                if broker_url is None:
                    raise ValueError("Broker URL Required")
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
        get_worker_cli(app)
        return broker
    return None


@singleton_function
def get_restful_api(app):
    from flask_restful import Api
    api = Api(app)
    return api


@singleton_function
def get_application(name: str, setting_object_path: str=None, setting_environment_variable: Optional[str]=None,
                    strict_slashes: bool=False,
                    default_error_handlers: bool=True,
                    setup_broker_func: Optional[Callable] = default_dramatiq_setup_broker,
                    setup_results_backend_func: Optional[Callable] = None,
                    template_folder='templates', app_version: str = '0.1',
                    swagger: bool = True, swagger_cors: bool = True) -> Flask:
    """
    Returns a Flask Application object. This function is a singleton function

    Args:
        name: Name of application we are defining
        setting_object_path:  Optional Python import path to the default settings objects
        setting_environment_variable: Optional environment variable that stores path to setting files
        strict_slashes: Should we use strict slashes(Ie a call to /projects will fail but a call to /projects will
            succeed
        default_error_handlers:
        setup_broker_func: Default function to setup a broker. By default we attempt to use Rabbit. Set to None to
            disable
        setup_results_backend_func: Function to call to setup the Results Backend. Default is None
        template_folder: Template folder
        app_version: Version of app to be used in Swagger definition
        swagger: Should we host a swagger.json that is generated at runtime from schemas defined using the schema_in,
            schema_out, and openapi_* decorators?
        swagger_cors: Should we enable CORS on that swagger.json endpoint?

    Returns:
        Flask APP
    """

    app = Flask(name, template_folder=template_folder)

    if HAS_RESTFUL:
        get_restful_api(app)
    if setting_object_path:
        app.logger.debug('Loading Application settings from {}'.format(setting_object_path))
        app.config.from_object(setting_object_path)
    if setting_environment_variable:
        app.logger.debug('Loading Application settings from the file {}'.format(setting_environment_variable))
        app.config.from_envvar(setting_environment_variable)
    app.url_map.strict_slashes = strict_slashes
    add_cli(app)

    if default_error_handlers:
        register_common_error_handlers(app)

    if HAS_DRAMATIQ and callable(setup_broker_func):
        app.broker = setup_broker_func(app)

        if callable(setup_results_backend_func):
            app.results_backend = setup_results_backend_func(app, app.broker)

    with app.app_context():
        if swagger:

            from .swagger import register_swagger, get_swagger_registry

            get_swagger_registry(name, app_version)
            app.config['swagger_cors'] = swagger_cors
            register_swagger(app)
            #if swagger_cors:
            #    app.cors = CORS(app, resources={r"/swagger.json": {"origins": "*"}})

        # register our helath check and show all our routes
        from .controllers import health_check_controller
    return app


if HAS_DRAMATIQ:
    from rse_api.tasks import dramatiq_parse_arguments, CRON_JOBS


    def start_dramatiq_workers(app):
        """
        Utility function to be used by cli to start workers

        Args:
            app: Flask app continaing the workers

        Returns:
            None
        """
        import dramatiq
        from dramatiq import cli as dm
        args = dramatiq_parse_arguments()
        args.module = None
        args.modules = []
        args.workers = []
        dm.parse_arguments = lambda: args
        dm.import_broker = lambda x: ('rse_api', app.broker)
        dm.main(args)

if HAS_APSCHEDULER:
    from apscheduler.schedulers.blocking import BlockingScheduler
    from rse_api.decorators import singleton_function

    def run_cron_workers(scheduler=BlockingScheduler):
        """
        CLI Function that runs only cron scheduled workers

        Args:
            scheduler: What scheduler to user. By default we use the BlockingScheduler

        Returns:
            None
        """
        logging.basicConfig(
            format="[%(asctime)s] [PID %(process)d] [%(threadName)s] [%(name)s] [%(levelname)s] %(message)s",
            level=logging.DEBUG,
        )

        # Pika is a bit noisy w/ Debug logging so we have to up its level.
        logging.getLogger("pika").setLevel(logging.WARNING)
        scheduler = scheduler()
        for trigger, module_path, func_name in CRON_JOBS:
            job_path = f"{module_path}:{func_name}.send"
            job_name = f"{module_path}.{func_name}"
            scheduler.add_job(job_path, trigger=trigger, name=job_name)

        def shutdown(signum, frame):
            scheduler.shutdown()

        signal.signal(signal.SIGINT, shutdown)
        signal.signal(signal.SIGTERM, shutdown)

        scheduler.start()


@singleton_function
def get_worker_cli(app: Flask) -> AppGroup:
    """
    Configures the workers CLI command group. By default this includes the commands

    - start --corn=True - Starts all workers(cron and actors)
    - list - List all workers
    - cron  - Run only cron workers

    Args:
        app: App to register cli on

    Returns:
        Worker CLI AppGroup
    """
    # Get flask db should have been called before this with any setup needed
    worker_cli = AppGroup('workers', help="Commands related to workers")

    if HAS_DRAMATIQ:

        @worker_cli.command('start', help="Starts all the workers including corn")
        @click.option('--cron', default=True, help='Whether we want to run cron jobs as well')
        def start_workers(cron):
            if HAS_APSCHEDULER and cron is True:
                from apscheduler.schedulers.background import BackgroundScheduler
                run_cron_workers(scheduler=BackgroundScheduler)

            start_dramatiq_workers(app)

        @worker_cli.command('list', help="Lists all the workers")
        def list_workers():
            import dramatiq
            workers = dramatiq.get_broker().get_declared_actors()
            workers = sorted(workers)
            print('Workers available: ')
            [print(worker) for worker in workers]

    if HAS_APSCHEDULER:

        @worker_cli.command('cron', help="Run any scheduled workers")
        def run_cron_only():
            run_cron_workers()

    app.cli.add_command(worker_cli)

    return worker_cli
