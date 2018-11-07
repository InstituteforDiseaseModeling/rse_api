from functools import wraps
from typing import Callable
from flask.views import MethodView
from rse_api.errors import RSEApiException
from rse_api.routing import register_api


def json_only(func):
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

    def decorator_register(func):
        if not issubclass(func, MethodView):
            raise RSEApiException("You can only register MethodView derived classes using this decorator")
        @wraps(func)
        def wrapper(*args, **kwargs):
            return func(*args, **kwargs)

        register_api(func, endpoint, url)
        return wrapper
    return decorator_register


def singleton_function(func: Callable) -> Callable:
    """
    Allows a function to run once then cache its results for later calls
    :param func: Function to be cached
    :return: Wrapper function
    """
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

    def timed(*args, **kwargs):
        start = time.time()
        result = func(*args, **kwargs)
        end = time.time()
        logger.debug('%r  %2.2f ms' % (func.__name__, (end - start) * 1000))
        return result
    return timed