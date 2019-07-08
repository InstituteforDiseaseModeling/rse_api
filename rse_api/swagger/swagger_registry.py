import hashlib
import json
import re
from collections import defaultdict
from enum import Enum
from typing import Union, Dict, Any, TextIO, Tuple

from flask import current_app, Flask
from marshmallow import Schema

from rse_api import singleton_function
from rse_api.swagger.swagger_spec import OpenApiPaths, OpenApiReference, OpenApiRequestBody, \
    OpenApiResponse, OpenApiDocument, OpenApiSchema, OpenApiPath, OpenApiComponents, OpenApiPathOperation, \
    OpenApiResponses, OpenApiInfo, OpenApiParameter, OpenApiDataType


class SwaggerSpecFormats(Enum):
    YAML = 'yaml'
    JSON = 'json'


def find_rule_by_url(app: Flask, url):
    for rule in app.url_map.iter_rules():
        if rule.endpoint == url:
            return rule.endpoint, rule.method
    return None


def find_view_func_by_url(app: Flask, url):
    rule = find_rule_by_url(app, url)
    if rule:
        view = app.view_functions.get(rule.endpoint)
        view.get(rule.method)
    return None



URL_VAR_PATTERN = re.compile(r'(\<.*?\>)', re.DOTALL)
URL_VAR_TYPE_REPLACE = re.compile(r'\<(.*?):(.*?)\>', re.DOTALL)


URL_TYPE_TO_OPENAPI_MAP = {
    'int': OpenApiDataType.INTEGER,
    'string': OpenApiDataType.STRING,
    'float': OpenApiDataType.NUMBER,
    'path': OpenApiDataType.STRING
}


def parameters_from_url(url):
        url_parameters = []

        for parameter in re.findall(URL_VAR_PATTERN, url):
            parameter = re.sub(r"[\<\>]", '', parameter)

            url_parameter = {
                "input_from": "path",
                "description": f'{parameter}',
                "required": True,
                "schema": {
                    "data_type": OpenApiDataType.STRING
                }
            }
            if ":" in parameter:
                parameter_type, parameter = parameter.split(":")
                if parameter_type not in URL_TYPE_TO_OPENAPI_MAP:
                    raise NotImplementedError("Cannot load the URL data type as Swagger parameter")

                url_parameter['schema'] = OpenApiSchema(data_type=URL_TYPE_TO_OPENAPI_MAP[parameter_type])


                url_parameter['name'] = parameter
                url_parameters.append(OpenApiParameter(**url_parameter))

        # fix the url references
        url = re.sub(URL_VAR_TYPE_REPLACE, r'{\2}', url)
        return url, url_parameters


class OpenApiRegistry:

    def __init__(self, name: str, version: Union[str, int, float]):
        """
        Used to build OpenAPI(Swagger) registry

        Args:
            name: Name of Application API we are building
            version:  Version of the application
        """
        self.components = OpenApiComponents()
        self.info = OpenApiInfo(name, version)
        self.class_definitions = defaultdict(lambda: defaultdict(dict))

        self.paths: Dict[str, OpenApiPath] = defaultdict(lambda: OpenApiPath())

        self.schema_functions = defaultdict(dict)

        # This holds a list of schema names to the cksum of their json representation
        # This allows us to generate names for schemas with different run-time differences
        # such as excluding fields
        self.marshmallow_schema_cksum = {}
        self.cksum_to_schema = {}

    def add_marshmallow_schema(self, marshmallow_schema: Schema, name: str = None,
                               from_marshmallow_options: Dict[str, Any] = None) -> Tuple[str, OpenApiSchema]:
        """
        Add a marshmallow schema to the OpenAPI Registry.


        Args:
            marshmallow_schema: Schema to add
            name: Name of schema in the open api. When the value of None, a name is calculated by using the class name
                with the word "Schema" will be  used. For example, *UserSchema* would be converted to User without the
                OpenApi.
            from_marshmallow_options: Options to pass to the *from_marshmallow* method

        Returns:
            A tuple containing the OpenApi name of schema and the OpenApiSchema object

        See Also:
            OpenApiSchema.from_marshmallow

        """
        name = name if name else type(marshmallow_schema).__name__.replace("Schema", "")
        if from_marshmallow_options is None:
            from_marshmallow_options = {}
        schema = OpenApiSchema.from_marshmallow(marshmallow_schema, **from_marshmallow_options)
        hasher = hashlib.md5()
        hasher.update(json.dumps(dict(schema), sort_keys=True).encode('utf-8'))
        schema_cksum = hasher.hexdigest()
        # select a new name if this one is taken by a different schema
        if schema_cksum in self.cksum_to_schema:
            name = self.cksum_to_schema[schema_cksum]
        if name in self.marshmallow_schema_cksum and self.marshmallow_schema_cksum[name] != schema_cksum:
            for i in range(1, 99999):
                new_name = f"{name}{i}"
                if new_name not in self.marshmallow_schema_cksum:
                    name = new_name
                    break
                # existing schema so
                elif self.marshmallow_schema_cksum[new_name] == schema_cksum:
                    return new_name, schema
        elif name in self.marshmallow_schema_cksum and self.marshmallow_schema_cksum[name] == schema_cksum:
            return name, schema

        self.marshmallow_schema_cksum[name] = schema_cksum
        self.cksum_to_schema[schema_cksum] = name

        self.add_schema(name, schema)
        return name, schema

    def add_schema(self, name: str, schema: OpenApiSchema):
        """
        Adds an OpenAPI schema to our registry

        Args:
            name: Name of schema
            schema: Schema object

        Returns:
            None
        """
        self.components.schemas[name] = schema

    def update_class_method_props(self, target_class: str, method_name: str, props: Dict):
        """
        Update an existing class definition method properties. See examples

        Some caution needs to be applied to this method because it does no validation of the data types.

        Args:
            target_class: Name of view/controller class we are documenting
            method_name:  Which HTTP/class method are we documenting
            props: Properties dictionary. Any proprerty passed in should be a valid property from the
                OpenApiPathOperation constructor and match the expected type for that constructor. For example,
                the parameters object expects a List of OpenApiParameter objects

        Examples:

        .. code-block:: python

        @register_resource(['/users'])
        class UserController(Resource):

            def get(self):
                pass

        get_swagger_registry().update_class_method_props('UserController', 'get',
            dict(description='A better description')
        )


        The preferred way to do the above is

        .. code-block:: python

        @register_resource(['/users'])
        class UserController(Resource):

            @openapi_operation_props(dict(description='A better description'))
            def get(self):
                pass


        Returns:
            None

        See Also:
            - OpenApiPathOperation.__init__
        """
        for k, v in props.items():
            self.class_definitions[target_class][method_name][k] = v

    def add_class_response(self, target_class: str, method_name:str , status_code: Union[int, str],
                           response: OpenApiResponse):
        """
        Add a response to a specific class method

        Args:
            target_class: Name of view/controller class we are documenting
            method_name:  Which HTTP/class method are we documenting
            status_code:  Status code for this response. Can also be the string "default"
            response: Response object for this response

        Returns:
            None
        """
        if 'responses' not in self.class_definitions[target_class][method_name]:
            self.class_definitions[target_class][method_name]['responses'] = {}
        self.class_definitions[target_class][method_name]['responses'][status_code] = response

    def add_class_request(self, target_class, method_name, request: Union[OpenApiReference, OpenApiRequestBody]):
        """
        Adds a request to a specific class method

        Args:
            target_class: Name of view/controller class we are documenting
            method_name:  Which HTTP/class method are we documenting
            request: Request object to add

        Returns:
            None
        """
        self.class_definitions[target_class][method_name]['request_body'] = request

    def render(self, file: Union[str, TextIO] = None, out_format=SwaggerSpecFormats.JSON) -> Dict:
        """
        Renders the schema to dictionary and optionally a yaml/json file
        Args:
            file: Optional Name of file or open file object to dummp contents to
            out_format: Format to dump to when writing to file objects

        Returns:
            Converted schema as dictionary
        """
        result = OpenApiDocument(info=self.info, paths=OpenApiPaths(self.paths), components=self.components)
        spec = dict(result)

        if file:
            if type(file) is str:
                file = open(file, 'w')
            # either use yaml or json library dump
            if out_format is SwaggerSpecFormats.YAML:
                import yaml
                olib = yaml
            else:
                olib = json
            olib.dump(spec, file)
            file.close()
        return spec

    def register_controller_resource(self, resource, name, urls, item_name=None):
        """
        Parses a controller class and finalized any class methods  that have been declared

        Args:
            resource: Resource(class) we are finalizing
            name: Name of the class
            urls: Urls that map onto the class
            item_name: Name of items the class represents. Only used in generation of definition like Deletes

        Returns:
            None
        """
        # Check if we have any specific definitions defined already

        # get list of methods for class
        # from rse_api import get_application
        # app = get_application()

        method_list = [func for func in dir(resource) if
                       func in ['get', 'post', 'put', 'delete', 'options', 'patch'] and callable(
                           getattr(resource, func))]
        for rule in current_app.url_map.iter_rules():
            # is this a url for our controller?
            if rule.rule in urls:
                new_url, parameters = parameters_from_url(rule.rule)
                url = new_url if len(parameters) else rule.rule
                self.paths[url] = OpenApiPath()
                for meth in method_list:
                    # do we have a class based definition for this?

                    if name in self.class_definitions and meth in self.class_definitions[name] \
                            and 'responses' in self.class_definitions[name][meth]:
                        # remap the definitions to proper path objects
                        op_props = self.class_definitions[name][meth]
                        if len(parameters) > 0:
                            if 'parameters' not in op_props:
                                op_props['parameters'] = []
                            op_props['parameters'] += parameters
                        op = OpenApiPathOperation(**self.class_definitions[name][meth])

                        self.paths[url].operations[meth] = op
                        del self.class_definitions[name][meth]
                    else:  # try to generate a definition ourselves
                        if meth == "delete":
                            item_str = item_name if item_name else "item"
                            a_or_an = "an" if item_str.lower()[0] in 'aeiou' else "a"
                            description = f"Delete {a_or_an} {item_str}"
                            op_props = dict(description=description)
                            if len(parameters) > 0:
                                op_props['parameters'] = parameters
                            if name in self.class_definitions and meth in self.class_definitions[name]:
                                op_props.update(self.class_definitions[name][meth])

                            op_props['responses'] = OpenApiResponses(status_codes={
                                204: OpenApiResponse("Deleted an item")
                            })
                            op = OpenApiPathOperation(**op_props)
                            self.paths[url].operations[meth] = op
                        else:
                            # we warn user here that we don't know have to document this api
                            pass


@singleton_function
def get_swagger_registry(name: str = 'rse_api', version='0.0.1') -> OpenApiRegistry:
    """
    Gets a copy of the global Swagger Registry
    Args:
        name: Name of application you want to "Swagger-ize"
        version: Version of that application

    Returns:
        A copy of the registry object
    """
    return OpenApiRegistry(name, version)
