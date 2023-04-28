import os
import time
from functools import wraps
from importlib import util
from logging import getLogger
from typing import Callable

from flask import jsonify
from flask.views import MethodView
from marshmallow import Schema

from .errors import RSEApiException
from .routing import register_api

HAS_APSCHEDULER = util.find_spec("apscheduler") is not None
HAS_DRAMATIQ = util.find_spec("dramatiq") is not None


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
            raise RSEApiException("Only JSON Requests are accepted")
        return func(*args, **kwargs)

    return wrapper


def singleton_function(func: Callable) -> Callable:
    """
    Allows a function to run once then cache its results for later calls
    :param func: Function to be cached
    :return: Wrapper function
    """

    @wraps(func)
    def wrapper(*args, **kwargs):
        if not hasattr(func, "has_ran"):
            setattr(func, "cache_value", func(*args, **kwargs))
            setattr(func, "has_ran", True)
        return getattr(func, "cache_value")

    return wrapper


def register_crud(endpoint, url=None) -> Callable:
    if url is None:
        url = endpoint

    def decorator_register(func: Callable) -> Callable:
        if not issubclass(func, MethodView):
            raise RSEApiException(
                "You can only register MethodView derived classes using this decorator"
            )

        @wraps(func)
        def wrapper(*args, **kwargs):
            return func(*args, **kwargs)

        register_api(func, endpoint, url)
        return wrapper

    return decorator_register


def register_resource(urls):
    from flask_restful import Resource

    from rse_api import get_restful_api

    api = get_restful_api()
    if type(urls) is tuple:
        urls = list(urls)

    elif type(urls) is str:
        urls = [urls]

    # from rse_api.swagger.swagger_spec import get_swagger

    def decorator_register_resource(func: Callable) -> Callable:
        if not issubclass(func, Resource):
            raise RSEApiException(
                f"You can only register Resource derived classes using this decorator."
                f" Please check {func.__name__}"
            )

        @wraps(func)
        def wrapper(*args, **kwargs):
            return func(*args, **kwargs)

        resource_args = tuple([func] + urls)
        api.add_resource(*resource_args)

        # process swagger after so urls have been registered
        # swagger = get_swagger()
        # swagger.process_class(func.__name__, urls)
        return wrapper

    return decorator_register_resource


def schema_in(
    schema: Schema,
    many: bool = False,
    instance_loader_func: Callable = None,
    partial: bool = False,
    description=None,
    example=None,
) -> Callable:
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

        # from rse_api.swagger.swagger_spec import get_swagger
        # swagger = get_swagger()
        # swagger_function = dict(function=func, partial=partial, many=many, in_schema=schema,
        #                        has_instance_loader_func=callable(instance_loader_func), description=description,
        #                        example=example)
        # swagger.add_schema_function(swagger_function)

        @wraps(func)
        @json_only
        def wrapper_schema_in(*args, **kwargs):
            body = request.json
            if callable(instance_loader_func):
                result = schema.load(
                    body,
                    many=many,
                    instance=instance_loader_func(*args, **kwargs),
                    partial=partial,
                )
            else:
                result = schema.load(body, many=many)
            if hasattr(result, "data"):
                args = (
                    tuple(list(args) + [result.data])
                    if args is not None
                    else (result.data,)
                )
            else:
                args = tuple(list(args) + [result]) if args is not None else (result,)
            return func(*args, **kwargs)

        return wrapper_schema_in

    return decorate_schema_in


def schema_out(
    schema: Schema, detect_many=True, many=False, description=None, example=None
) -> Callable:
    """
    Decorator that attempts to convert the output of the wrapped function with a Flask JSON Response using the
    supplied Marshmallow schema

    :param schema: Marshmallow schema to convert output of function to
    :param detect_many: Detect if output should be many(lists)
    :param many: Only needed if detect many is False. Mainly set the except many output
    :return: Wrapped function
    """

    def decorate_schema_out(func: Callable):
        # from rse_api.swagger.swagger_spec import get_swagger

        # swagger = get_swagger()
        # swagger_function = dict(function=func, detect_many=detect_many, many=many, out_schema=schema, example=example,
        #                        description=description)
        # swagger.add_schema_function(swagger_function)

        @wraps(func)
        def wrapper_schema_out(*args, **kwargs):
            result = func(*args, **kwargs)
            imany = (detect_many and type(result) is list) or many
            result = schema.dump(result, many=imany)
            if hasattr(result, "data"):
                return jsonify(result.data)
            else:
                return jsonify(result)

        return wrapper_schema_out

    return decorate_schema_out


def schema_in_out(
    schemaIn: Schema,
    schemaOut: Schema,
    schema_in_many=False,
    schema_out_many=False,
    schema_out_detect_many: bool = True,
    schema_in_loader_func: Callable = None,
    schema_in_partial: bool = False,
    description=None,
    in_example=None,
    out_example=None,
) -> Callable:
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
        # from rse_api.swagger.swagger_spec import get_swagger

        # swagger = get_swagger()
        # swagger_function = dict(function=func, detect_many=schema_out_detect_many, in_many=schema_in_many,
        #                        many=schema_out_many, partial=schema_in_partial,
        #                        instance_loader_func=callable(schema_in_loader_func), in_schema=schemaIn,
        #                        description=description, in_example=in_example, out_example=out_example,
        #                        out_schema=schemaOut)
        # swagger.add_schema_function(swagger_function)

        @wraps(func)
        @schema_in(
            schemaIn,
            schema_in_many,
            instance_loader_func=schema_in_loader_func,
            partial=schema_in_partial,
        )
        @schema_out(schemaOut, many=schema_out_many, detect_many=schema_out_detect_many)
        def wrapper(*args, **kwargs):
            return func(*args, **kwargs)

        return wrapper

    return decorate_schema_in_out


def timeit_logged(func: Callable) -> Callable:
    """
    Times the execution of a function and log to the Timed log
    :param func: Function that should be timed
    :return: Wrapped function
    """
    logger = getLogger("timing")

    @wraps(func)
    def timed(*args, **kwargs):
        start = time.time()
        result = func(*args, **kwargs)
        end = time.time()
        logger.debug("%r  %2.2f ms" % (func.__name__, (end - start) * 1000))
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
        if os.environ.get("FLASK_ENV", "production") == "documentation":
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
            if not hasattr(actor, "fn") and callable(actor):
                actor = dramatiq.actor(actor)
            module_path = actor.fn.__module__
            func_name = actor.fn.__name__
            CRON_JOBS.append((trigger, module_path, func_name))
            return actor

        return decorator
