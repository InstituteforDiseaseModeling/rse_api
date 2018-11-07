import time
from functools import wraps
from logging import getLogger
from typing import Callable

from flask import jsonify
from flask.views import MethodView
from marshmallow import Schema

from rse_api.errors import RSEApiException
from rse_api.routing import register_api


def json_only(func: Callable):
    @wraps(func)
    def wrapper(*args, **kwargs):
        from flask import request
        if not request.is_json:
            raise RSEApiException('Only JSON Requests are accepted')
        return func(*args, **kwargs)
    return wrapper


def register_crud(endpoint, url=None):
    if url is None:
        url = endpoint

    def decorator_register(func: Callable):
        if not issubclass(func, MethodView):
            raise RSEApiException("You can only register MethodView derived classes using this decorator")
        @wraps(func)
        def wrapper(*args, **kwargs):
            return func(*args, **kwargs)

        register_api(func, endpoint, url)
        return wrapper
    return decorator_register


def schema_in(schema: Schema, many: bool=False):

    def decorate_schema_in(func: Callable):
        from flask import request

        @wraps(func)
        @json_only
        def wrapper_schema_in(*args, **kwargs):
            body = request.json
            result = schema.load(body, many=many)
            args = tuple(list(args) + [result.data]) if args is not None else (result.data,)
            return func(*args, **kwargs)
        return wrapper_schema_in
    return decorate_schema_in


def schema_out(schema: Schema, many=False):
    def decorate_schema_out(func: Callable):
        @wraps(func)
        def wrapper_schema_out(*args, **kwargs):
            result = func(*args, **kwargs)
            return jsonify(schema.dump(result, many=many).data)
        return wrapper_schema_out
    return decorate_schema_out


def schema_in_out(schemaIn: Schema, schemaOut: Schema, schema_in_many=False,
                  schema_out_many=False):
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
        if not hasattr(wrapper,'has_ran'):
            setattr(wrapper, 'has_ran', True)
            setattr(wrapper, 'cache_value', func(*args, **kwargs))
        return getattr(wrapper, 'cache_value')
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