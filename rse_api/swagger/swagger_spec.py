import json
import os
import re
from collections import defaultdict
from enum import Enum
from typing import Dict, Any, TextIO, Union, List

import yaml
from flask import Flask
from marshmallow import Schema, fields
from rse_api.decorators import singleton_function


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


REFERENCE_PATH = "#/components/schemas/"


class SwaggerSpecFormats(Enum):
    YAML = 'yaml'
    JSON = 'json'


class SwaggerSpec:
    def __init__(self):
        path = os.path.dirname(os.path.abspath(__file__))
        self.data = json.load(open(os.path.join(path, 'base_schema.json'), 'r'))
        self.definitions = {}
        self.paths = defaultdict(dict)
        self.class_map = {}
        self.url_expr = re.compile(r'(\<.*?\>)', re.DOTALL)
        self.url_replace = re.compile(r'\<(.*?):(.*?)\>', re.DOTALL)
        # This should hold a dict of dicts
        self.function_map = defaultdict(dict)

    def set_version(self, version):
        self.data['version'] = version

    def set_title(self, title):
        self.data['title'] = title

    def set_description(self, description):
        self.data['description'] = description

    def set_terms_of_service(self, tos):
        self.data['termsOfService'] = tos

    def set_host(self, servers: List[str]):
        self.data['servers'] = servers

    def set_base_path(self, path):
        self.data['basePath'] = path

    def set_contact_info(self, name, email, url=None):
        self.data['contact'] = dict(
            name=name,
            email=email
        )
        if url:
            self.data['url'] = url

    def add_definition(self, obj_class: Schema):
        self.definitions[obj_class.__name__] = obj_class

    def add_schema_function(self, swagger_data: Dict[str, Any]):
        # parse class name from the name
        target_func = swagger_data['function']
        if 'decorate' not in target_func.__qualname__:
            cls_name, method = target_func.__qualname__.split('.')

            data = dict(
                class_name=cls_name,
                method=method,
                arguments=target_func.__code__.co_varnames,
                defaults=target_func.__defaults__
            )
            data.update({k: v for k, v in swagger_data.items() if k not in ['function']})

            self.function_map[cls_name][method] = data

    def add_class_to_map(self, cls, url):
        self.class_map[cls] = url

    def parameters_from_url(self, url, obj_string):
        url_parameters = []

        for parameter in re.findall(self.url_expr, url):
            parameter = re.sub(r"[\<\>]", '', parameter)
            url_parameter = {
                "in": "path",
                "description": f'ID Of {obj_string}',
                "required": True,
                "schema": {
                    "type": "string"
                }
            }
            if ":" in parameter:
                parameter_type, parameter = parameter.split(":")
                url_parameter['schema']['type'] = parameter_type
                if url_parameter['schema']['type'] == "int":
                    url_parameter['schema']['type'] = 'integer'
                # Do this here so that we touch any without types
                url_parameter['name'] = parameter
                url_parameters.append(url_parameter)

        return url_parameters

    def schema_to_definition(self, definition_name, schema):
        swagger_definition = {'type': 'object', 'properties': {}, 'required': []}

        for field_name, field in schema.fields.items():
            if field_name not in schema.exclude:
                pr_field = None
                # Update the required fields
                if field.required:
                    swagger_definition['required'].append(field.name)

                field_type = type(field)
                if field_type in [fields.String, fields.Str, fields.Email, fields.UUID, fields.DateTime, fields.Date,
                                  fields.LocalDateTime, fields.Url, fields.URL, fields.Raw]:

                    pr_field = {
                        "type": "string"
                    }
                    if field_type in [fields.DateTime, fields.Date, fields.LocalDateTime]:
                        pr_field['format'] = 'date' if field_type is fields.Date else 'date-time'
                    elif field_type in [fields.URL, fields.Url]:
                        pr_field['format'] = 'uri'
                    elif field_type is fields.UUID:
                        pr_field['format'] = 'uuid'
                    # how do we define byte or binary fields?

                elif field_type in [fields.Integer, fields.Int]:
                    pr_field = {
                        "type": "integer"
                    }

                elif field_type in [fields.Float, fields.Decimal, fields.Number, fields.FormattedString]:
                    pr_field = {
                        "type": "number"
                    }
                elif field_type in [fields.Boolean, fields.Bool]:
                    pr_field = {
                        "type": "boolean"
                    }
                elif field_type in [fields.Nested, fields.List, fields.Dict]:
                    field_schema = None

                    if field_type is fields.List:
                        if type(field.container) is fields.Nested:
                            # lookup object name
                            field_schema = field.container.nested.__class__.__name__.replace('Schema', '')
                            if field_schema not in self.definitions:
                                self.definitions[field_schema] = field.container.nested, self.schema_to_definition(
                                    field_schema, field.container.nested)
                    else:
                        if field.nested == "self":
                            field_schema = definition_name
                    pr_field = {
                        "type": "object" if field_type is fields.Nested else "array"
                    }
                    if field_schema:
                        pr_field['items'] = {
                            'type': 'object',
                            '$ref': f"{REFERENCE_PATH}{field_schema}"
                        }
                else:
                    pr_field = {
                        "type": field_type.__name__
                    }
                    pass

                if pr_field:
                    swagger_definition['properties'][field.name] = pr_field

        return swagger_definition

    def add_path_method(self, url, method, operation_id=None, parameters=None, in_schema=None, out_schema=None,
                        description=None, many=True, errors=None, autogen_url_parameters=True):
        if method not in self.paths[url]:
            if in_schema:
                obj_string = in_schema.__class__.__name__.replace('Schema', '')
            elif out_schema:
                obj_string = out_schema.__class__.__name__.replace('Schema', '')
            else:
                obj_string = None
            if description is None:
                if obj_string is None:
                    raise NotImplementedError("Cannot auto-generate description without an input schema or an output "
                                              "schema")

                if method == "get" and out_schema and many:
                    description = f"Returns all {obj_string}s from the system that the user has access to."
                elif method == "get" and not many:
                    description = f"Returns a {obj_string} based on an id."
                elif method == "post" and in_schema:
                    description = f"Creates a  {obj_string}"
                elif method == "put" and in_schema and not many:
                    description = f"Update a {obj_string} based on an id and user supplied input."
                elif method == "delete" and not many:
                    description = f"Delete a {obj_string} based on id"

            if operation_id is None:
                if method == "get" and out_schema and many:
                    operation_id = f"findAll{obj_string}s"
                elif method == "get" and out_schema:
                    operation_id = f"find{obj_string}sById"
                elif method == "post":
                    operation_id = f"add{obj_string}ById"
                elif method == "put" and in_schema and not many:
                    operation_id = f"update{obj_string} based on an id and user supplied input."
                elif method == "delete" and not many:
                    operation_id = f"remove{obj_string} based on id"

            if parameters is None:
                # try to parse parameters from url
                parameters = []

            if len(parameters) == 0 or autogen_url_parameters:
                parameters += self.parameters_from_url(url, obj_string)

            responses = {}
            if out_schema:
                swagger_schema = {
                    "$ref": f"{REFERENCE_PATH}{obj_string}"
                }

                if many:
                    responses[200] = dict(description=f"List of {obj_string}s response", content=dict(
                        {
                            'application/json': dict(schema={
                                "type": "array",
                                "items": swagger_schema
                            })
                        }
                    ))
                    if obj_string not in self.definitions:
                        self.definitions[obj_string] = out_schema, self.schema_to_definition(obj_string, out_schema)
                else:
                    responses[200] = dict(description=f"{obj_string} response",
                                          content=dict(
                                              {
                                                  'application/json': dict(
                                                      schema=swagger_schema
                                                  )
                                              }
                                          ))

            request_body = None
            if in_schema:

                action = 'add' if method == 'post' else 'update'
                obj_prefix = 'new' if method == 'post' else 'partial'

                swagger_obj_name = obj_string
                if obj_string in self.definitions:
                    if len(in_schema.exclude) != len(self.definitions[obj_string][0].exclude):
                        swagger_obj_name = f'{obj_prefix}{obj_string}'

                swagger_schema = {
                    "$ref": f"{REFERENCE_PATH}{swagger_obj_name}"
                }

                request_body = {
                    "description": f'{obj_string} to {action}',
                    "required": True,
                    "content": {
                        'application/json': {
                            'schema': swagger_schema
                        }
                    }
                }

                if swagger_obj_name not in self.definitions:
                    self.definitions[swagger_obj_name] = in_schema, self.schema_to_definition(swagger_obj_name,
                                                                                              in_schema)

            # check url to make sure we shouldn't replace part of it
            url = re.sub(self.url_replace, r'{\2}', url)

            responses['default'] = dict(description="unexpected error",
                                        content=dict(
                                            {
                                                'application/json': dict(
                                                    schema={"$ref": f"{REFERENCE_PATH}Error"}
                                                )
                                            }
                                        )
                                        )
            path_method = dict(
                description=description,
                operationId=operation_id,
                parameters=parameters,
                responses=responses
            )
            if request_body:
                path_method['requestBody'] = request_body

            self.paths[url][method] = path_method

    def process_class(self, class_name, urls, exclude_put_without_id=True):
        if class_name in self.function_map:
            from rse_api import get_application
            app = get_application()

            for rule in app.url_map.iter_rules():
                if rule.rule in urls:
                    # now check if this url has entry in our function map
                    for method in [r.lower() for r in rule.methods]:
                        if method in self.function_map[class_name]:
                            if method == "put" and len(rule.arguments) == 0:
                                continue
                            api_details = self.function_map[class_name][method]
                            if 'out_schema' in api_details and 'in_schema' in api_details:
                                many = (api_details['detect_many'] and len(rule.arguments) == 0) or api_details['many']
                                path_props = dict(in_schema=api_details['in_schema'],
                                                  out_schema=api_details['out_schema'],
                                                  many=many)
                                self.add_path_method(rule.rule, method, **path_props)
                            elif 'out_schema' in api_details:
                                many = (api_details['detect_many'] and len(rule.arguments) == 0) or api_details['many']
                                self.add_path_method(rule.rule, method, out_schema=api_details['out_schema'],
                                                     many=many)
                            elif 'in_schema' in api_details:
                                self.add_path_method(rule.rule, method, in_schema=api_details['in_schema'])

    def generate_swagger_spec(self, file: Union[str, TextIO] = None,
                              out_format: SwaggerSpecFormats = SwaggerSpecFormats.JSON):
        spec = {
        }

        spec.update(self.data)
        spec.update(dict(paths=self.paths))
        spec.update(dict(
            components=dict(
                schemas={k: v[1] for k, v in self.definitions.items()}
            )
        ))
        spec['components']['schemas']['Error'] = {
            'type': 'object',
            'properties': dict(code={'type': 'integer'}, message={'type': 'string'}),
            'required': ['code', 'message']
        }

        if file:
            if type(file) is str:
                file = open(file, 'w')
            # either use yaml or json library dump
            olib = yaml if out_format is SwaggerSpecFormats.YAML else json
            olib.dump(spec, file)
            file.close()
        return spec


@singleton_function
def get_swagger() -> SwaggerSpec:
    return SwaggerSpec()
