import os
import time
from functools import wraps
from importlib import util
from logging import getLogger
from typing import Callable
from flask import jsonify, Response
from flask.views import MethodView
from marshmallow import Schema


from .errors import RSEApiException
from .routing import register_api

HAS_APSCHEDULER = util.find_spec('apscheduler') is not None
HAS_DRAMATIQ = util.find_spec('dramatiq') is not None


def json_only(func: Callable) -> Callable:
    """
    Wraps a method to only support requests that are json

    :param func: Function to wrap
    :return: wrapped function
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        from flask import request
        if not request.is_json:
            raise RSEApiException('Only JSON Requests are accepted')
        return func(*args, **kwargs)
    return wrapper


def register_crud(endpoint, url=None) -> Callable:
    if url is None:
        url = endpoint

    def decorator_register(func: Callable) -> Callable:
        if not issubclass(func, MethodView):
            raise RSEApiException("You can only register MethodView derived classes using this decorator")

        @wraps(func)
        def wrapper(*args, **kwargs):
            return func(*args, **kwargs)

        register_api(func, endpoint, url)
        return wrapper
    return decorator_register


def register_resource(urls):
    from rse_api import get_restful_api
    from flask_restful import Resource
    api = get_restful_api()
    if type(urls) is tuple:
        urls = list(urls)

    elif type(urls) is str:
        urls = [urls]

    def decorator_register_resource(func: Callable) -> Callable:
        if not issubclass(func, Resource):
            raise RSEApiException(f"You can only register Resource derived classes using this decorator."
                                  f" Please check {func.__name__}")

        @wraps(func)
        def wrapper(*args, **kwargs):
            return func(*args, **kwargs)
        resource_args = tuple([func] + urls)
        api.add_resource(*resource_args)
        return wrapper
    return decorator_register_resource


def schema_in(schema: Schema, many: bool=False) -> Callable:
    """
    Decorator that converts the flask json input data into a parsed data from a supplied schema object

    :param schema: Marshmallow schema to parse flask request with. It is recommended to use strict mode schemas
    :param many: Is the input expecting many objects?
    :return: Wrapped function
    """

    def decorate_schema_in(func: Callable):
        from flask import request

        @wraps(func)
        @json_only
        def wrapper_schema_in(*args, **kwargs):
            body = request.json
            result = schema.load(body, many=many)
            if hasattr(result, 'data'):
                args = tuple(list(args) + [result.data]) if args is not None else (result.data,)
            else:
                args = tuple(list(args) + [result]) if args is not None else (result,)
            return func(*args, **kwargs)
        return wrapper_schema_in
    return decorate_schema_in


def schema_out(schema: Schema, many=False) -> Callable:
    """
    Decorator that attempts to convert the output of the wrapped function with a Flask JSON Response using the
    supplied Marshmallow schema

    :param schema: Marshmallow schema to convert output of function to
    :param many: Is the output expecting many objects?
    :return: Wrapped function
    """
    def decorate_schema_out(func: Callable):
        @wraps(func)
        def wrapper_schema_out(*args, **kwargs):
            result = func(*args, **kwargs)
            result = schema.dump(result, many=many)
            if hasattr(result, 'data'):
                return jsonify(schema.dump(result, many=many).data)
            else:
                return jsonify(result)
        return wrapper_schema_out
    return decorate_schema_out


def schema_in_out(schemaIn: Schema, schemaOut: Schema, schema_in_many=False, schema_out_many=False) -> Callable:
    """
    Decorator for methods that take a schema result and return a object that will be serialized to a specific schema

    schemaIn is the source schema. The schema attempts to load data from flask.request. It is recommend you make this
    schema strict to throw exceptions on errors

    :param schemaIn: Marshmallow schema to parse flask request with. It is recommended to use strict mode schemas
    :param schemaOut: Marshmallow schema to convert output of function to
    :param schema_in_many: Is the input expecting many objects?
    :param schema_out_many: Is the output expecting many objects?
    :return: Wrapped function
    :rtype: Callable
    """
    def decorate_schema_in_out(func: Callable):
        @wraps(func)
        @schema_in(schemaIn, schema_in_many)
        @schema_out(schemaOut, schema_out_many)
        def wrapper(*args, **kwargs):
            return func(*args, **kwargs)

        return wrapper
    return decorate_schema_in_out


def singleton_function(func: Callable) -> Callable:
    """
    Allows a function to run once then cache its results for later calls
    :param func: Function to be cached
    :return: Wrapper function
    """

    @wraps(func)
    def wrapper(*args, **kwargs):
        if not hasattr(func, 'has_ran'):
            setattr(func, 'cache_value', func(*args, **kwargs))
            setattr(func, 'has_ran', True)
        return getattr(func, 'cache_value')
    return wrapper


def timeit_logged(func: Callable) -> Callable:
    """
    Times the execution of a function and log to the Timed log
    :param func: Function that should be timed
    :return: Wrapped function
    """
    logger = getLogger('timing')

    @wraps(func)
    def timed(*args, **kwargs):
        start = time.time()
        result = func(*args, **kwargs)
        end = time.time()
        logger.debug('%r  %2.2f ms' % (func.__name__, (end - start) * 1000))
        return result
    return timed


def actor(*args, **kwargs) -> Callable:
    """
    Wrapper for dramtiq actor decorator to ensure we have stub broker during docuemntation
    Args:
        func:

    Returns:

    """
    import dramatiq

    def decorate_wrap_actor(func: Callable):

        if os.environ.get('FLASK_ENV', 'production') == 'documentation':
            from dramatiq.brokers.stub import StubBroker
            broker = StubBroker()
            dramatiq.set_broker(broker)

        return dramatiq.actor(*args, **kwargs)(func)
    return decorate_wrap_actor

if HAS_APSCHEDULER and HAS_DRAMATIQ:
    import dramatiq
    from apscheduler.triggers.cron import CronTrigger

    CRON_JOBS = []  # Global Cron Jobs

    def cron(crontab: str) -> Callable:
        """Wrap a Dramatiq actor in a cron schedule.

        :param crontab: Cron tab string - see https://apscheduler.readthedocs.io/en/latest/modules/triggers/cron.html
        """
        trigger = CronTrigger.from_crontab(crontab)

        def decorator(actor: Callable) -> Callable:
            if not hasattr(actor, 'fn') and callable(actor):
                actor = dramatiq.actor(actor)
            module_path = actor.fn.__module__
            func_name = actor.fn.__name__
            CRON_JOBS.append((trigger, module_path, func_name))
            return actor

        return decorator
