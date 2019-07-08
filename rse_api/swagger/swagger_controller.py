import functools
import json
from flask import current_app
from flask_cors import cross_origin

from rse_api.decorators import conditional_decorator
from rse_api.swagger import get_swagger_registry


@functools.lru_cache(maxsize=2)
def get_cached_json() -> str:
    """
    Fetch the OpenApiSchema as json. Cache the results after first call
    Returns:
        Json string representing the OpenApiSchema for application
    """
    return json.dumps(get_swagger_registry().render())


@current_app.route('/swagger.json')
@conditional_decorator(cross_origin(), current_app.config.get('swagger_cors', False))
def get_swagger_json():
    """
    Default swagger controller to be included in rse apps. By default we are cross origin allowing
    other clients to at least get our API definition

    Returns:
        Cached Schema as JSON
    """
    return get_cached_json()


