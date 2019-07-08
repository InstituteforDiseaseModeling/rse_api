import os
import time
from functools import wraps
from importlib import util
from logging import getLogger
from typing import Callable, List, Union
from flask import jsonify
from marshmallow import Schema
from .tasks import CRON_JOBS
from .errors import RSEApiException

HAS_APSCHEDULER = util.find_spec('apscheduler') is not None
HAS_DRAMATIQ = util.find_spec('dramatiq') is not None


def json_only(func: Callable) -> Callable:
    """
    Decorator that validates that a request is JSON or otherwise errors

    Args:
        func: Function to wrap

    Raises:
        - RSEApiException if the request is not of type json

    Returns:
        Wrapped function
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        from flask import request
        if not request.is_json:
            raise RSEApiException('Only JSON Requests are accepted')
        return func(*args, **kwargs)
    return wrapper


def singleton_function(func: Callable) -> Callable:
    """
    Allows a function to run one then cache its result for later calls
    Args:
        func:

    Returns:
        Wrapped fimctopm
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        if not hasattr(func, 'has_ran'):
            setattr(func, 'cache_value', func(*args, **kwargs))
            setattr(func, 'has_ran', True)
        return getattr(func, 'cache_value')
    return wrapper


def conditional_decorator(decorator: Callable, condition: Union[bool, Callable]) -> Callable:
    """
    Only decorate function if condition is true. This is useful when allowing decorator based features such as OpenApi
    configurable by the user based on options.

    Args:
        decorator: The decorator to run if condition is true
        condition: Condition value

    Examples:
        In the below example, the get method will have Cross Origin applied to it if the flask current_app
        object's env setting is either dev or development

        .. code-block:: python

            class UserResource(Resource):
                @conditional_decorator(cross_origin(), current_app.env in ['dev', 'development'])
                def get(self):
                    pass


        Here is another example using a function. This will only enable the swagger operation update if we have another
        swagger definition before this one

        .. code-block:: python

            # returns true if we have swagger definitions before users
            def get_swagger_config():
                if current_app.env in ['dev', 'development']:
                    reg = get_swagger_registry()
                    return len(reg.paths) > 1
                return False

            class UserResource(Resource):

                @conditional_decorator(open_api_operation_props(description="Example"), get_swagger_config)
                def get(self):
                    pass

    Returns:
        Wrapped function
    """
    def decorate_conditional_decorator(func: Callable):
        # If we have a function and it evaluates to true or we have True, decorate the function
        if (callable(condition) and condition()) or condition:
            return decorator(func)
        else:
            return func
    return decorate_conditional_decorator


def register_resource(urls: Union[str, List[str]], generate_swagger: bool = True) -> Callable:
    """
    Register a Flask Restful Resource to listen on specified urls

    Args:
        urls:
        generate_swagger: Should this resource be included in the OpenApi(Swagger) documentation

    See Also:
        - https://flask-restful.readthedocs.io/en/latest/quickstart.html#resourceful-routing
        - :meth:`rse_api.decorators.schema_in`
        - :meth:`rse_api.decorators.schema_in_out`
        - :meth:`rse_api.decorators.schema_out`

    Returns:
        Wrapped function
    """
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

        # process swagger after so urls have been registered
        if generate_swagger:
            from rse_api.swagger.swagger_controller import get_swagger_registry
            swagger = get_swagger_registry()
            swagger.register_controller_resource(func, func.__name__, urls)
        return wrapper
    return decorator_register_resource


def schema_in(schema: Schema, many: bool=False, instance_loader_func: Callable=None,
              partial: bool = False, swagger: bool = True) -> Callable:
    """
    Decorator that converts the flask json input data into a parsed data from a supplied schema object


    Args:
        schema: An instance of a Marshmallow Schema object that will be used to parse the input data's body
        many: Controls whether input is expected to be an array of items or a single item of type Schena. Defaults to
            *False*.
        instance_loader_func: Function that takes the args for the endpoint and uses those to load an instance.
            Usually this is used for PUTs to load and instance by id. See the PUT Example below
        partial: To be used when a function is provided . If so, we support partial loads on puts. This means that the
            user can supply single field updates since the db instance will be loaded.
        swagger: Should this schema and request body be added to OpenApi Documentation?
    Examples:
        .. code-block:: python

            from flask_restful import Resource
            from marshmallow import fields, Schema
            from rse_api.decorators import schema_in
            from marshmallow_sqlalchemy import ModelSchema
            from rse_db.utils import get_db, get_declarative_base
            from rse_db.data_patterns import IdMixin, CreatedAndUpdatedAtMixin

            Base = get_declarative_base()

            # Our DB Model. It includes an autoincrementing id and Created/Updated timestamp fields
            # We also add some basic Find, and Write functionality through RSEBasicReadWriteModel
            class UserModel(IdMixin, CreatedAndUpdatedAtMixin, RSEBasicReadWriteModel, Base):
                __tablename__ = 'users'
                username = Column(Text, nullable=False)

            # Vanilla marshmallow schema
            # that will allow ensure input data matches schema
            class UserSchema(Schema):
                username = fields.String(required=True)

            # Smart schema that will load automatically convert schema parsed content
            # into a specified db Model
            class SmartUserSchema(ModelSchema):
                username = fields.String(required=True)

                class Meta:
                    model = TaskTag
                    # We use get_db here vs db to reduce the chance of import loops
                    # see documentation on get_db
                    sqla_session = get_db().session

            default_in_schema = UserSchema(exclude=[id])

            @register_resource(['/users', '/users/<int:id>'])
            class UserController(Resource):

                # The below will dump a a parsed schema object
                @schema_in(default_in_schema)
                def post(self, data):
                    # we should save our data and then return
                    return data.data

                # The below we dump the input data minus any id field passed through the body
                @schema_in(default_in_schema)
                def put(self, id, data):
                    # we should load exiting data using id
                    # then merge in the new data from our input
                    # then save it
                    return data.data


            sm_in_schema = SmartUserSchema(exclude=[id])
            sm_out_schema = SmartUserSchema()

            @register_resource(['/sm', '/sm/<int:id>'])
            class SmartUserController(Resource):

                @schema_out(sm_out_schema)
                def get(self, id=None):
                    if id is None:
                        return UserModel.query.all()
                    else:
                        return UserModel.find_one(id)

                # This will load our data as an instance of UserModel ready to be committed
                @schema_in_out(sm_in_schema, sm_out_schema)
                def post(self, data):
                    # We get an instance of UserModel which has a commit function thanks to
                    # RSEBasicReadWriteModel
                    return data.commit()

                # This will be load the data based on the input from the URL being based
                # to UserModel.find_one, if that succeeds we should get a UserModel back
                # with the updates ready to be saved
                @schema_in_out(sm_in_schema, sm_out_schema, instance_loader_func=UserModel.find_one, partial=True)
                def put(self, data):
                    return data.commit()

                def delete(self, id):
                    UserModel.delete_by_pk(id)
                    return '', 204


    Returns:
        Wrapped function
    """
    def decorate_schema_in(func: Callable):
        from flask import request

        from rse_api.swagger.decorators import openapi_request

        @conditional_decorator(openapi_request(schema), swagger)
        @wraps(func)
        @json_only
        def wrapper_schema_in(*args, **kwargs):
            body = request.json
            if callable(instance_loader_func):
                result = schema.load(body, many=many, instance=instance_loader_func(*args, **kwargs), partial=partial)
            else:
                result = schema.load(body, many=many)
            if hasattr(result, 'data'):
                args = tuple(list(args) + [result.data]) if args is not None else (result.data,)
            else:
                args = tuple(list(args) + [result]) if args is not None else (result,)
            return func(*args, **kwargs)
        return wrapper_schema_in
    return decorate_schema_in


def schema_out(schema: Schema, detect_many=True, many=False, generate_swagger=True) -> Callable:
    """
    Decorator that attempts to convert the output of the wrapped function with a Flask JSON Response using the
    supplied Marshmallow schema. In addition, if generate_swagger is True, the schema will be added to the OpenApi
    schema for the app.

    Args:
        schema: Marshmallow schema to convert output of function to
        detect_many: Detect many will attempt to detect if the output is of type List or single item. Useful in
            endpoints that support both List[Type] and Type
        many:  Only needed if detect many is False. Mainly set the except many output
        generate_swagger: Should we generate swagger documentation for this item. This will add a response to a
            specific OpenApiPathOperation

    Returns:
        Wrapped function
    """
    def decorate_schema_out(func: Callable):
        array_response = None
        if generate_swagger:
            from rse_api.swagger.decorators import openapi_response, swagger
            from rse_api.swagger.swagger_spec import OpenApiSchema, OpenApiDataType, OpenApiReference
            cs = openapi_response(schema)
            if many:
                schema_name, os_schema = swagger.add_marshmallow_schema(schema)
                schema_ref = OpenApiReference.to_schema(schema_name)

                array_response = openapi_response(OpenApiSchema(OpenApiDataType.ARRAY, items=schema_ref),
                                                  description=f"List of {schema_name}s")

        @conditional_decorator(cs if not array_response else array_response, generate_swagger)
        @wraps(func)
        def wrapper_schema_out(*args, **kwargs):
            result = func(*args, **kwargs)
            imany = (detect_many and type(result) is list) or many
            result = schema.dump(result, many=imany)
            if hasattr(result, 'data'):
                return jsonify(result.data)
            else:
                return jsonify(result)
        return wrapper_schema_out
    return decorate_schema_out


def schema_in_out(schemaIn: Schema, schemaOut: Schema, schema_in_many=False, schema_out_many=False,
                  schema_out_detect_many: bool=True, schema_in_loader_func: Callable = None,
                  schema_in_partial: bool=False) -> Callable:
    """
    Decorator for methods that take a schema result and return a object that will be serialized to a specific schema

    schemaIn is the source schema. The schema attempts to load data from flask.request. It is recommend you make this
    schema strict to throw exceptions on errors

    Args:
        schemaIn: Marshmallow schema to parse flask request with. It is recommended to use strict mode schemas
        schemaOut: Marshmallow schema to convert output of function to
        schema_in_many: Is the input expecting many objects?
        schema_out_many: Many option of schema_out
        schema_out_detect_many: Detect many option of schema_out
        schema_in_loader_func: in_loader_func of schema_in
        schema_in_partial: Partial option on schema_in

    See Also:
        - :meth:`rse_api.decorators.schema_in`
        - :meth:`rse_api.decorators.schema_out`
    Returns:
        Wrapped Function
    """
    def decorate_schema_in_out(func: Callable):
        @schema_in(schemaIn, schema_in_many, instance_loader_func=schema_in_loader_func, partial=schema_in_partial)
        @schema_out(schemaOut, many=schema_out_many, detect_many=schema_out_detect_many)
        @wraps(func)
        def wrapper(*args, **kwargs):
            return func(*args, **kwargs)

        return wrapper
    return decorate_schema_in_out


def timeit_logged(func: Callable) -> Callable:
    """
    Decorator that allows you to time a function. The timing will be printed to logger debug

    Args:
        func: Function to time

    Returns:
        Wrapped function
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
    Wrapper for dramtiq actor decorator to ensure we have stub broker during documentation
    Args:
        *args: Arguments to pass to dramatiq.actor
        **kwargs: Key Word arguments to pass to dramatiq.actor

    Returns:
        Wrapped function

    See Also:
        - https://dramatiq.io/_modules/dramatiq/actor.html
    """
    import dramatiq

    def decorate_wrap_actor(func: Callable):

        if os.environ.get('FLASK_ENV', 'production') == 'documentation':
            from dramatiq.brokers.stub import StubBroker
            broker = StubBroker()
            dramatiq.set_broker(broker)

        return dramatiq.actor(*args, **kwargs)(func)
    return decorate_wrap_actor


# If we have ApScheduler and Dramatiq, then define cron decorator
if HAS_APSCHEDULER and HAS_DRAMATIQ:
    import dramatiq
    from apscheduler.triggers.cron import CronTrigger

    def cron(crontab: str) -> Callable:
        """
        Wrap a Dramatiq actor in a cron schedule.

        Args:
            crontab: Cron string

        Notes:
            see https://apscheduler.readthedocs.io/en/latest/modules/triggers/cron.html
        Returns:
            Wrapped actor
        See Also:
            - https://crontab.guru/
            - https://apscheduler.readthedocs.io/en/latest/modules/triggers/cron.html
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
