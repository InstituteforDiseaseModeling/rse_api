from functools import wraps
from typing import Callable, Union, Dict, List, Any

from marshmallow import Schema

from rse_api.swagger import get_swagger_registry
from rse_api.swagger.swagger_spec import OpenApiResponse, OpenApiReference, OpenApiSchema, \
    OpenApiMediaType, OpenApiRequestBody

swagger = get_swagger_registry()


def openapi_response(response_obj: Union[OpenApiResponse, Schema, OpenApiSchema, OpenApiReference],
                     path: str = None,
                     description: str = None,
                     content_types:List[str] = None,
                     status_code: Union[str, int] = None,
                     autodetect_http_code: bool = True, from_marshmallow_options: Dict[str, Any] = None) -> Callable:
    """
    Decorator that Adds an OpenAPI Response to a specific Path or Method

    Args:
        response_obj: Type of Response Object. This can be either an OpenApiResponse or a Reference. If it is an
            OpenApiSchema or Marshmallow Schema, an Response object will be built including those
        path: Optional path. If not included, this must be used on a Resource class method like get, post, etc
        description: Optional Description for the response
        content_types:  Optional list of content types this supports. By default, if this is None, application/json is
            assumed. This content type along with either a OpenApiSchema, OpenApiReference or Marshmallow Schema are
            using to build an OpenMediaType object
        status_code: Status code for response. Not needed if autodetect_http_code is true
        autodetect_http_code: Detect http status code from method name. If method is post, a 201 is assumed. For get
            and put we return 200 and lastly for delete we return a 204
        from_marshmallow_options: Optional dictionary set of arguments to pass to OpenApiSchema.from_marshmallow when
            converting a Marshmallow Schema to an OpenApi schema
    Returns:
        Wrapped Functions

    See Also:
        - :meth:`rse_api.swagger.swagger_spec.OpenApiSchema.from_marshmallow`
    """

    if content_types is None:
        content_types = ['application/json']

    def decorate_openapi_response(func: Callable):
        target_class = None
        if "." in func.__qualname__:
            target_class, method_name = func.__qualname__.split(".")
        else:
            method_name = func.__name__

        media_types = {}
        st = status_code
        response_description = description
        if isinstance(response_obj, Schema):
            schema_name, schema = swagger.add_marshmallow_schema(response_obj,
                                                                 from_marshmallow_options=from_marshmallow_options)
            schema_ref = OpenApiReference.to_schema(schema_name)
            for ct in content_types:
                media_types[ct] = OpenApiMediaType(schema_ref)

            # Build a description if we don't have one as input
            if response_description is None:
                schema_proper_name = schema_name.replace("Schema", "")
                response_description = f"{schema_proper_name} response"
            response = OpenApiResponse(response_description, content=media_types)

        elif isinstance(response_obj, (OpenApiSchema, OpenApiReference)):
            # Build a description if we don't have one as input
            if response_description is None:
                schema_proper_name = response_obj.__name__.replace("Schema", "")
                response_description = f"{schema_proper_name} response"

            for ct in content_types:
                media_types[ct] = OpenApiMediaType(response_obj)
            response = OpenApiResponse(response_description, content=media_types)
        else:
            response = response_obj

        # build our status code if that option is set
        if autodetect_http_code:
            if method_name == "post":
                st = 201
            elif method_name in ["get", "put"]:
                st = 200
            elif method_name == "delete":
                st = 204

        # if we know the target class, registry method there for later rendering
        if target_class:
            swagger.add_class_response(target_class, method_name, st, response)
        elif path:
            swagger.add_path_response(path, st, response)

        @wraps(func)
        def wrapper(*args, **kwargs):
            return func(*args, **kwargs)

        return wrapper
    return decorate_openapi_response


def openapi_operation_props(**kwargs) -> Callable:
    """
    Update an OpenApiOperation properties that is part of a Resource Class

    Args:
        **kwargs: Functions to past to OpenApiOperation init function

    Returns:
        Wrapped function

    See Also:
        - :meth:`rse_api.swagger.swagger_spec.OpenApiOperation.__init__`
    """

    def decorate_openapi_operation(func: Callable):
        target_class = None
        if "." in func.__qualname__:
            target_class, method_name = func.__qualname__.split(".")
        else:
            method_name = func.__name__

        swagger.update_class_method_props(target_class, method_name, props=kwargs)

        @wraps(func)
        def wrapper(*args, **kwargs):
            return func(*args, **kwargs)
        return wrapper

    return decorate_openapi_operation


def openapi_request(request_obj: Union[OpenApiReference, OpenApiRequestBody, Schema],
                        path: str = None, description: str = None, content_types: List[str] = None) -> Callable:
    """
    Decorator that builds add a request to a path or class

    Args:
        request_obj: Object to be used a request. If the object is
            - An OpenApiReference or OpenApiRequestBody, they are used directly
            - If the object is a Marshmallow Schema, the schema is converted to an OpenApiSchema and then that
                is used to build an OpenApiResponse
        path: Optional path. Needed when using without Resource Classes(ie app.route)
        description: Description of the Request
        content_types: List of content types the response applies to. Defaults to 'application/json'

    Returns:
        Wrapped Function
    """

    if content_types is None:
        content_types = ['application/json']

    def decorate_openapi_request(func: Callable):
        target_class = None
        if "." in func.__qualname__:
            target_class, method_name = func.__qualname__.split(".")
        else:
            method_name = func.__name__

        media_types = {}
        if isinstance(request_obj, Schema):
            request_description = description
            schema_name, schema = swagger.add_marshmallow_schema(request_obj)
            schema_ref = OpenApiReference.to_schema(schema_name)
            for ct in content_types:
                media_types[ct] = OpenApiMediaType(schema_ref)

            # Build a description if we don't have one as input
            if request_description is None:
                schema_proper_name = schema_name.replace("Schema", "")
                response_description = f"{schema_proper_name} request"
                request = OpenApiResponse(response_description, content=media_types)

        else:
            request = request_obj

        # if we know the target class, registry method there for later rendering
        if target_class:
            swagger.add_class_request(target_class, method_name, request)
        #elif path:
        #    swagger.add_path_request(path, request)

        @wraps(func)
        def wrapper(*args, **kwargs):
            return func(*args, **kwargs)

        return wrapper
    return decorate_openapi_request

