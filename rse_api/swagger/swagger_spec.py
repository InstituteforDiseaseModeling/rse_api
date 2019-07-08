from abc import ABC
from enum import Enum
from typing import Dict, Any, Union, List
import stringcase
from marshmallow import Schema, fields, validate

REFERENCE_PATH = "#/components/schemas/"


class IgnoreNoneIterMixin(ABC):
    """
    IgnoreNoneIterMixin adds an iter function to the specified object that allows easy conversion to dict
    by casting (dict(x)). The iter will ignore any fields that are None by default

    In an addition, it provided three properties to control the behaviour of field conversion

    First is excluded fields, This is a list of properties of the object that will be excluded when iterating over an
    object.

    Next is required fields. This ia a list of properties that we always want in our output.
    Last is remapped fields which will remap field names when converting to a dict.
    """

    @property
    def excluded_fields(self) -> List[str]:
        return []

    @property
    def required_fields(self) -> List[str]:
        return []

    @property
    def remapped_fields(self) -> Dict[str, str]:
        return {}

    def __iter__(self):
        for field in self.required_fields:
            fname = field if field not in self.remapped_fields else self.remapped_fields[field]
            v = getattr(self, field)
            if type(v) in [list, dict]:
                v = nested_convert(v)
            elif isinstance(v, IgnoreNoneIterMixin):
                v = dict(v)
            yield fname, v

        excluded_fields = self.excluded_fields + self.required_fields
        for k, v in vars(self).items():
            if k not in excluded_fields and not k.startswith("___"):
                if v is not None:
                    if type(v) in [list, dict]:
                        v = nested_convert(v)
                    elif isinstance(v, IgnoreNoneIterMixin):
                        v = dict(v)
                    fname = k if k not in self.remapped_fields else self.remapped_fields[k]
                    yield fname, v


class OpenApiReference(IgnoreNoneIterMixin):

    def __init__(self, reference: str):
        """

        Args:
            reference: REQUIRED. The reference string.

        See Also:
             - https://github.com/OAI/OpenAPI-Specification/blob/master/versions/3.0.0.md#referenceObject
        """
        self.reference = reference

    @property
    def remapped_fields(self):
        return dict(reference='$ref')

    @classmethod
    def to_component_type(cls, name, to_type):
        return OpenApiReference(reference=f'#/components/{to_type}/{name}')

    @classmethod
    def to_schema(cls, name):
        return cls.to_component_type(name, 'schemas')


class OpenApiContact(IgnoreNoneIterMixin):
    @property
    def required_fields(self) -> List[str]:
        return []

    def __init__(self, name: str = None, url: str = None, email: str = None):
        """

        Args:
            name:
            url:
            email:

        See Also:
            https://github.com/OAI/OpenAPI-Specification/blob/master/versions/3.0.0.md#contact-object
        """
        self.name: str = name
        self.url: str = url
        self.email: str = email


class OpenApiLicense(IgnoreNoneIterMixin):
    def __init__(self, name: str, url: str = None):
        """

        Args:
            name: The license name used for the API.
            url: A URL to the license used for the API. MUST be in the format of a URL.

        See Also:
            - https://github.com/OAI/OpenAPI-Specification/blob/master/versions/3.0.0.md#license-object-example
        """
        self.name = name
        self.url: str = url

    @property
    def required_fields(self) -> List[str]:
        return ['name']


class OpenApiInfo(IgnoreNoneIterMixin):

    def __init__(self, title: str, version: str, description: str = None, terms_of_service: str = None,
                 api_license: OpenApiLicense = None, contact: OpenApiContact = None):
        """

        Args:
            title: REQUIRED. The title of the application.
            version: REQUIRED. The version of the OpenAPI document (which is distinct from the OpenAPI Specification version or the API implementation version).
            description:A short description of the application. CommonMark syntax MAY be used for rich text representation.
            terms_of_service: A URL to the Terms of Service for the API. MUST be in the format of a URL.
            api_license: The license information for the exposed API.
            contact: The contact information for the exposed API.

        See Also:
            https://github.com/OAI/OpenAPI-Specification/blob/master/versions/3.0.0.md#infoObject
        """
        self.title: str = title
        self.description: str = description
        self.terms_of_service: str = terms_of_service
        self.api_license: OpenApiLicense = api_license
        self.version: str = version
        self.contact: OpenApiContact = contact

    @property
    def remapped_fields(self):
        return dict(terms_of_service='termsOfService', api_license='license')

    @property
    def required_fields(self) -> List[str]:
        return ['title', 'version']


class OpenApiSecurityType(Enum):
    APIKEY = "apiKey"
    HTTP = "http"
    OAUTH = "oauth2"
    OPEN_ID_CONNECT = "openIdConnect"


OpenApiSecurityType_Require_MAP = {
    OpenApiSecurityType.APIKEY: ['name', 'input_from'],

}


class OpenApiSecurityInputFrom(Enum):
    QUERY = "query"
    HEADER = "header"
    COOKIE = "cookie"


class OpenApiOAuthFlow(IgnoreNoneIterMixin):
    def __init__(self, authorization_url: str, token_url: str, scopes: Dict[str, str], refresh_url: str = None):
        """

        Args:
            authorization_url: REQUIRED. The authorization URL to be used for this flow. This MUST be in the form of a
                URL.
            token_url: REQUIRED. The token URL to be used for this flow. This MUST be in the form of a URL.
            scopes: REQUIRED. The available scopes for the OAuth2 security scheme. A map between the scope name and a
                short description for it.
            refresh_url: The URL to be used for obtaining refresh tokens. This MUST be in the form of a URL.

        See Also:
            - https://github.com/OAI/OpenAPI-Specification/blob/master/versions/3.0.0.md#oauthFlowObject
        """
        self.authorization_url = authorization_url
        self.token_url = token_url
        self.scopes = scopes
        self.refresh_url = refresh_url

    @property
    def remapped_fields(self):
        return dict(authorization_url='authorizationUrl', token_url='tokenUrl', refresh_url='refreshUrl')


class OpenApiOAuthFlows(IgnoreNoneIterMixin):
    def __init__(self, implicit: OpenApiOAuthFlow = None, password: OpenApiOAuthFlow = None,
                 client_credentials: OpenApiOAuthFlow = None, authorization_code: OpenApiOAuthFlow = None):
        """

        Args:
            implicit: Configuration for the OAuth Implicit flow
            password: Configuration for the OAuth Resource Owner Password flow
            client_credentials: Configuration for the OAuth Client Credentials flow. Previously called application in
                OpenAPI 2.0.
            authorization_code: Configuration for the OAuth Authorization Code flow. Previously called accessCode in
                OpenAPI 2.0.

        See Also:
            - https://github.com/OAI/OpenAPI-Specification/blob/master/versions/3.0.0.md#oauthFlowsObject
        """
        self.implicit = implicit
        self.password = password
        self.client_credentials = client_credentials
        self.authorization_code = authorization_code

    @property
    def remapped_fields(self):
        return dict(client_credentials='clientCredentials', authorization_code='authorizationCode')


class OpenApiSecurity(IgnoreNoneIterMixin):
    def __init__(self, security_type: OpenApiSecurityType, description: str = None, name: str = None,
                 input_from: OpenApiSecurityInputFrom = None, schema: str = None, bearer_format: str = None,
                 flows: OpenApiOAuthFlows = None, open_id_connect_url: str = None):
        """

        Args:
            security_type: 	REQUIRED. The type of the security scheme. Valid values are "apiKey", "http", "oauth2",
                "openIdConnect".
            description: A short description for security scheme. CommonMark syntax MAY be used for rich text
                representation.
            name: REQUIRED when type is apiKey. The name of the header, query or cookie parameter to be used.
            input_from: REQUIRED when type is apiKey. The location of the API key. Valid values are "query", "header"
                or "cookie"
            schema: REQUIRED when type is http. The name of the HTTP Authorization scheme to be used in the
                Authorization header as defined in RFC7235.
            bearer_format: A hint to the client to identify how the bearer token is formatted. Bearer tokens are
                usually generated by an authorization server, so this information is primarily for documentation
                purposes. Only needed when type is HTTP
            flows: REQUIRED when type is oAuth. An object containing configuration information for the flow types
                supported.
            open_id_connect_url: REQUIRED when type is OpenIdConnect. OpenId Connect URL to discover OAuth2
                configuration values. This MUST be in the form of a URL.

        See Also:
            - https://github.com/OAI/OpenAPI-Specification/blob/master/versions/3.0.0.md#securitySchemeObject
        """

        self.open_id_connect_url = open_id_connect_url
        self.flows = flows
        self.bearer_format = bearer_format
        self.schema = schema
        self.input_from = input_from
        self.name = name
        self.description = description
        self.security_type = security_type

        self.__validate_security_type(security_type, OpenApiSecurityType_Require_MAP[self.security_type])

    def __validate_security_type(self, security_type: OpenApiSecurityType, security_fields: List[str]):
        if any([getattr(self, x) is None for x in security_fields]):
            raise ValueError(f"The fields {','.join(security_fields)} are required for type {security_type.value}")


class OpenApiExternalDocumentation(IgnoreNoneIterMixin):
    def __init__(self, url: str, description: str = None):
        """

        Args:
            url: REQUIRED. The URL for the target documentation. Value MUST be in the format of a URL.
            description: A short description of the target documentation. CommonMark syntax MAY be used for rich text
                representation.
        """
        self.url = url
        self.description = description

    @property
    def required_fields(self):
        return ['url']


class OpenApiTag(IgnoreNoneIterMixin):
    def __init__(self, name: str, description: str = None, external_docs: OpenApiExternalDocumentation = None):
        """

        Args:
            name: REQUIRED. The name of the tag.
            description: A short description for the tag. CommonMark syntax MAY be used for rich text representation.
            external_docs: Additional external documentation for this tag.

        See Also:
            - https://github.com/OAI/OpenAPI-Specification/blob/master/versions/3.0.0.md#tagObject
        """
        self.name = name
        self.description = description
        self.external_docs = external_docs

    @property
    def remapped_fields(self):
        return dict(external_docs='externalDocs')

    @property
    def required_fields(self):
        return ['name']


class OpenApiServerVariable(IgnoreNoneIterMixin):
    def __init__(self, default: str, enum: List[str] = None, description: str = None):
        """

        Args:
            default: REQUIRED. The default value to use for substitution, and to send, if an alternate value is not
            supplied. Unlike the Schema Object's default, this value MUST be provided by the consumer.
            enum: An enumeration of string values to be used if the substitution options are from a limited set.
            description: An optional description for the server variable. CommonMark syntax MAY be used for rich text
             representation.

        See Also:
            - https://github.com/OAI/OpenAPI-Specification/blob/master/versions/3.0.0.md#serverVariableObject
        """
        self.default = default
        self.enum = enum
        self.description = description

    @property
    def required_fields(self):
        return ['default']


class OpenApiServer(IgnoreNoneIterMixin):
    def __init__(self, url: str, description: str = None, variables: Dict[str, OpenApiServerVariable] = None):
        """

        Args:
            url: REQUIRED. A URL to the target host. This URL supports Server Variables and MAY be relative, to
            indicate that the host location is relative to the location where the OpenAPI document is being served.
            Variable substitutions will be made when a variable is named in {brackets}.
            description: 	An optional string describing the host designated by the URL. CommonMark syntax MAY be
            used for rich text representation.
            variables: A map between a variable name and its value. The value is used for substitution in the server's
            URL template.

        See Also
            https://github.com/OAI/OpenAPI-Specification/blob/master/versions/3.0.0.md#serverObject
        """
        self.url = url
        self.description = description
        self.variables = variables

    @property
    def required_fields(self):
        return ['url']


class OpenApiLink(IgnoreNoneIterMixin):
    def __init__(self, operation_ref: str = None, operation_id: str = None, parameters: Dict[str, Any] = None,
                 request_body: any = None, description: str = None, server: OpenApiServer = None):
        """

        Args:
            operation_ref: A relative or absolute reference to an OAS operation. This field is mutually exclusive of
                the operationId field, and MUST point to an Operation Object. Relative operationRef values MAY be used
                to locate an existing Operation Object in the OpenAPI definition.
            operation_id: The name of an existing, resolvable OAS operation, as defined with a unique operationId.
                This field is mutually exclusive of the operationRef field.
            parameters: A map representing parameters to pass to an operation as specified with operationId or
                identified via operationRef. The key is the parameter name to be used, whereas the value can be a
                constant or an expression to be evaluated and passed to the linked operation. The parameter name can be
                qualified using the parameter location [{in}.]{name} for operations that use the same parameter name in
                different locations (e.g. path.id).
            request_body: A literal value or {expression} to use as a request body when calling the target operation.
            description: A description of the link. CommonMark syntax MAY be used for rich text representation.
            server: A server object to be used by the target operation.

        See Also:
            - https://github.com/OAI/OpenAPI-Specification/blob/master/versions/3.0.0.md#linkObject
        """
        self.operation_ref = operation_ref
        self.operation_id = operation_id
        self.parameters = parameters
        self.request_body = request_body
        self.description = description
        self.server = server

    @property
    def remapped_fields(self):
        return dict(request_body='requestBody', operation_ref='operationRef', operation_id='operationId')


class OpenApiExample(IgnoreNoneIterMixin):

    def __init__(self, summary: str = None, description: str = None, value: str = None, external_value: str = None):
        self.summary = summary
        self.description = description
        self.value = value
        self.external_value = external_value

    @property
    def remapped_fields(self):
        return dict(external_value='externalValue')


class OpenApiHeader(IgnoreNoneIterMixin):

    def __init__(self, description: str = None, required: bool = False, deprecated: bool = False,
                 allow_empty: bool = False):
        """

        Args:
            description:  A brief description of the parameter. This could contain examples of use. CommonMark syntax
                MAY be used for rich text representation.
            required: Determines whether this parameter is mandatory.
            deprecated: Specifies that a parameter is deprecated and SHOULD be transitioned out of usage.
            allow_empty: Sets the ability to pass empty-valued parameters. This is valid only for query parameters and
                allows sending a parameter with an empty value. Default value is false. If style is used, and if
                 behavior is n/a (cannot be serialized), the value of allowEmptyValue SHALL be ignored.

        See Also:
            - https://github.com/OAI/OpenAPI-Specification/blob/master/versions/3.0.0.md#headerObject
        """
        self.description = description
        self.required = required
        self.deprecated = deprecated
        self.allow_empty = allow_empty

    @property
    def remapped_fields(self):
        return dict(allow_empty='allowEmptyValue')


class OpenApiEncoding(IgnoreNoneIterMixin):

    def __init__(self, content_type: str, headers: Dict[str, Union[OpenApiReference, OpenApiHeader]] = None,
                 style: str = None, explode: bool = True, allow_reserved=False):
        """

        Args:
            content_type: The Content-Type for encoding a specific property. Default value depends on the property
                type: for string with format being binary – application/octet-stream; for other primitive types –
                text/plain; for object - application/json; for array – the default is defined based on the inner type.
                The value can be a specific media type (e.g. application/json), a wildcard media type (e.g. image/*),
                or a comma-separated list of the two types.
            headers: A map allowing additional information to be provided as headers, for example Content-Disposition.
                Content-Type is described separately and SHALL be ignored in this section.
                This property SHALL be ignored if the request body media type is not a multipart.
            style: Describes how a specific property value will be serialized depending on its type. See Parameter
                Object for details on the style property. The behavior follows the same values as query parameters,
                including default values. This property SHALL be ignored if the request body media type is not
                application/x-www-form-urlencoded.
            explode: When this is true, property values of type array or object generate separate parameters for each
                value of the array, or key-value-pair of the map. For other types of properties this property has no
                effect. When style is form, the default value is true. For all other styles, the default value is
                false. This property SHALL be ignored if the request body media type is not
                application/x-www-form-urlencoded.
            allow_reserved: Determines whether the parameter value SHOULD allow reserved characters, as defined by
                RFC3986 :/?#[]@!$&'()*+,;= to be included without percent-encoding. The default value is false. This
                property SHALL be ignored if the request body media type is not application/x-www-form-urlencoded.

        See Also:
            - https://github.com/OAI/OpenAPI-Specification/blob/master/versions/3.0.0.md#encodingObject
        """
        self.content_type = content_type
        self.headers = headers,
        self.style = style
        self.explode = explode
        self.allow_reserved = allow_reserved

    @property
    def remapped_fields(self):
        return dict(content_type='contentType', allow_reserved='allowReserved')


class OpenApiDataType(Enum):
    """
    See Also:
        - http://json-schema.org/latest/json-schema-core.html#rfc.section.4.2.1
    """
    BOOL = 'boolean'
    OBJECT = 'object'
    ARRAY = 'array'
    NUMBER = 'number'
    STRING = 'string'
    INTEGER = 'integer'

    def __repr__(self):
        return self.value


class OpenApiStringFormats(Enum):
    """
    # https://github.com/OAI/OpenAPI-Specification/blob/master/versions/3.0.0.md#data-types
    """
    DATETIME = 'date-time'
    EMAIL = 'email'
    HOSTNAME = 'hostname'
    IPV4 = 'ipv4'
    IPV6 = 'ipv6'
    URI = 'uri'
    BYTE = 'byte'
    BINARY = 'binary'
    DATE = 'date'
    PASSWORD = 'password'


class OpenApiIntFormats(Enum):
    """
    # https://github.com/OAI/OpenAPI-Specification/blob/master/versions/3.0.0.md#data-types
    """
    INT32 = 'int32'
    INT64 = 'int64'


class OpenApiNumberFormats(Enum):
    """
    # https://github.com/OAI/OpenAPI-Specification/blob/master/versions/3.0.0.md#data-types
    """
    FLOAT = 'float'
    DOUBLE = 'double'


OpenApiDataTypeFormatMap = {
    OpenApiDataType.STRING: OpenApiStringFormats,
    OpenApiDataType.INTEGER: OpenApiIntFormats,
    OpenApiDataType.NUMBER: OpenApiNumberFormats,
}


class OpanApiSchemaCombineType(Enum):
    """
    https://json-schema.org/understanding-json-schema/reference/combining.html#combining-schemas
    """
    ALLOF = 'allOf'
    ANYOF = 'anyOf'
    ONEOF = 'ontOf'
    NOT = 'NOT'


schema_types = Union['OpenApiSchema', 'OpenApiSchemaCombine', 'OpenApiReference']

OpenApiSchemaValidFieldsByType = {
    OpenApiDataType.STRING: ['pattern', 'min_length', 'max_length', 'format'],
    OpenApiDataType.INTEGER: ['exclusive_maximum', 'minimum', 'exclusive_minimum', 'multiple_of', 'maximum'],
    OpenApiDataType.NUMBER: ['exclusive_maximum', 'minimum', 'exclusive_minimum', 'multiple_of', 'maximum'],
    OpenApiDataType.OBJECT: ['properties', 'additional_properties', 'required_properties', 'dependencies',
                             'min_properties',
                             'max_properties'],
    OpenApiDataType.ARRAY: ['items', 'additional_items', 'min_items', 'max_items', 'unique_items'],
    OpenApiDataType.BOOL: []

}


class OpenApiSchema(IgnoreNoneIterMixin):

    def __init__(self, data_type: Union[OpenApiDataType, List[OpenApiDataType]], multiple_of: float = None,
                 maximum: float = None,
                 exclusive_maximum: float = None, minimum: float = None, exclusive_minimum: float = None,
                 pattern: str = None, format: OpenApiStringFormats = None, min_length: int = None,
                 max_length: int = None,
                 properties: Dict[str, schema_types] = None,
                 additional_properties=False, required_properties: List[str] = None,
                 dependencies: Dict[str, List[str]] = None, min_properties: int = None, max_properties: int = None,
                 items: Union[schema_types, List[schema_types]] = None,
                 additional_items: List[Any] = None, min_items: int = None, max_items: int = None,
                 unique_items: bool = False, enum: List[any] = None, const: str = None, title: str = None,
                 description: str = None, default: Any = None, examples: List[Any] = None):
        """

        Args:
            data_type:
            multiple_of:

        See Also:
             - https://json-schema.org/understanding-json-schema/reference/numeric.html
             - https://json-schema.org/understanding-json-schema/reference/string.html
        """
        self.data_type = [data_type] if data_type and type(data_type) is OpenApiDataType else data_type
        # https://json-schema.org/understanding-json-schema/reference/numeric.html#multiples
        self.multiple_of = multiple_of
        # https://json-schema.org/understanding-json-schema/reference/numeric.html#range
        self.maximum = maximum
        self.exclusive_maximum = exclusive_maximum
        self.minimum = minimum
        self.exclusive_minimum = exclusive_minimum
        # https://json-schema.org/understanding-json-schema/reference/string.html#regular-expressions
        self.pattern = pattern
        # https://json-schema.org/understanding-json-schema/reference/string.html#format
        self.format = format
        # https://json-schema.org/understanding-json-schema/reference/string.html#length
        self.min_length = min_length
        self.max_length = max_length
        # https://json-schema.org/understanding-json-schema/reference/object.html#properties
        self.properties = properties
        self.additional_properties = additional_properties
        # https://json-schema.org/understanding-json-schema/reference/object.html#required-properties
        self.required_properties = required_properties
        # https://json-schema.org/understanding-json-schema/reference/object.html#property-dependencies
        self.dependencies = dependencies
        # https://json-schema.org/understanding-json-schema/reference/object.html#size
        self.min_properties = min_properties
        self.max_properties = max_properties

        # https://json-schema.org/understanding-json-schema/reference/array.html#items
        self.items = items
        self.additional_items = additional_items
        # https://json-schema.org/understanding-json-schema/reference/array.html#length
        self.min_items = min_items
        self.max_items = max_items
        # https://json-schema.org/understanding-json-schema/reference/array.html#uniqueness
        self.unique_items = unique_items

        # https://json-schema.org/understanding-json-schema/reference/generic.html#enumerated-values
        self.enum = enum

        # https://json-schema.org/understanding-json-schema/reference/generic.html#constant-values
        if const:
            self.enum = [const]

        # https://json-schema.org/understanding-json-schema/reference/generic.html#metadata
        self.title = title
        self.description = description
        self.default = default
        self.examples = examples

        num_only = ['exclusive_maximum', 'minimum', 'exclusive_minimum', 'multiple_of', 'maximum']
        num_types = [OpenApiDataType.NUMBER.value, OpenApiDataType.INTEGER.value]

        num_fields = {num_field: getattr(self, num_field) for num_field in num_only \
                      if getattr(self, num_field) is not None}
        if num_fields and all([t not in num_types for t in self.data_type]):
            error_fields = ", ".join([stringcase.titlecase(field) for field in num_fields])
            field_str = "field" if len(num_fields) == 1 else "fields"
            raise ValueError(
                f"The {field_str} {error_fields} can only be used with {' and '.join(num_types)} data types.")

        str_only = ['pattern', 'min_length', 'max_length']
        str_fields = {str_field: getattr(self, str_field) for str_field in str_only \
                      if getattr(self, str_field) is not None}
        if str_fields and all([t != OpenApiDataType.STRING for t in self.data_type]):
            error_fields = ", ".join([stringcase.titlecase(field) for field in str_fields])
            field_str = "field" if len(num_fields) == 1 else "fields"
            raise ValueError(
                f"The {field_str} {error_fields} can only be used with STRING data types.")

        # validate format vs string/ double etc

        obj_only = ['properties', 'additional_properties', 'required_properties', 'dependencies', 'min_properties',
                    'max_properties']

        array_only = ['items', 'additional_items', 'min_items', 'max_items', 'unique_items']

    @classmethod
    def get_type_map_for(cls, types, dest_type: OpenApiDataType) -> Dict[fields.Field, OpenApiDataType]:
        type_map = {}
        for t in types:
            type_map[t] = dest_type
        return type_map

    @classmethod
    def from_marshmallow(cls, schema: Schema, description: str = None, extra_exclude: List[str] = None):
        from .swagger_registry import get_swagger_registry
        extra_exclude = extra_exclude if extra_exclude else []
        # first determine the data type of the schema
        str_types = [fields.Date, fields.DateTime, fields.Url, fields.LocalDateTime, fields.UUID,
                     fields.FormattedString, fields.Email, fields.String, fields.Str, fields.Raw]
        type_map = cls.get_type_map_for(str_types, OpenApiDataType.STRING)
        type_map.update(cls.get_type_map_for([fields.Int, fields.Integer], OpenApiDataType.INTEGER))
        type_map.update(cls.get_type_map_for([fields.Float, fields.Decimal, fields.Number], OpenApiDataType.NUMBER))
        type_map.update(cls.get_type_map_for([fields.Boolean, fields.Bool], OpenApiDataType.BOOL))
        type_map.update(cls.get_type_map_for([fields.Nested, fields.Dict], OpenApiDataType.OBJECT))
        type_map[fields.List] = OpenApiDataType.ARRAY

        property_map = {
            fields.Date:
                {'format': 'date'}
            ,
            fields.DateTime: {'format': 'date-time'},
            fields.LocalDateTime: {'format': 'date-time'},
            fields.UUID: {
                "format": "uuid"
            },
            fields.Email: {
                "format": "email"
            }
        }

        props: Dict[str, schema_types] = {}
        required = []

        full_exclude = list(schema.exclude) + list(extra_exclude)
        for name, field in schema.fields.items():
            if name in full_exclude:
                continue
            field_schema = None
            field_props = {}
            open_api_date_type = None
            data_type = type(field)

            if 'description' in field.metadata:
                field_props['description'] = field.metadata['description']

            # check if the field is required
            if field.required:
                required.append(name)

            if data_type in type_map:
                open_api_date_type = type_map[data_type]

            if data_type is fields.List:

                if type(field.container) is fields.Nested:
                    fmo = {}
                    if getattr(field, 'exclude', None):
                        fmo = dict(extra_exclude=field.exclude)
                    sub_name, sub_schema = get_swagger_registry().add_marshmallow_schema(field.container.nested,
                                                                                         from_marshmallow_options=fmo)
                    field_props['items'] = OpenApiReference.to_schema(sub_name)

            for validator in field.validators:
                v_type = type(validator)
                if data_type in [fields.Str, fields.String, fields.Email, fields.FormattedString]:
                    if v_type is validate.Length:
                        if validator.min:
                            field_props['min_length'] = validator.min
                        if validator.max:
                            field_props['max_length'] = validator.max

            if getattr(field, 'default', None):
                field_props['default'] = field.default

            # if the type is nested, give a direct link to the reference type
            if data_type is fields.Nested:
                fmo = {}
                if getattr(field, 'exclude', None):
                    fmo = dict(extra_exclude=field.exclude)
                if field.nested != "self":
                    sub_name, sub_schema = get_swagger_registry().add_marshmallow_schema(field.schema,
                                                                                         from_marshmallow_options=fmo)
                else:
                    sub_name = '{self}'
                field_schema = OpenApiReference.to_schema(sub_name)

            # grab default properties for type
            if data_type in property_map:
                field_props.update(property_map[data_type])

            if field_schema is None:
                field_schema = OpenApiSchema(open_api_date_type, **field_props)
            props[name] = field_schema

        # if field in str_types:
        if description is None and getattr(schema.Meta, 'description', None):
            description = getattr(schema.Meta, 'description')
        schema = OpenApiSchema(OpenApiDataType.OBJECT, properties=props, required_properties=required,
                               description=description)
        return schema

    @property
    def remapped_fields(self):
        return dict(data_type='type', multiple_of='multipleOf', exclusive_maximum='exclusiveMaximum',
                    exclusive_minimum='exclusiveMinimum', min_length='minLength', max_length='maxLength',
                    additional_properties='additionalProperties', required_properties='requiredProperties',
                    min_properties='minProperties', max_properties='maxProperties',
                    additional_items='additionalItems', min_items='minItems', max_items='maxItems',
                    unique_items='uniqueItems')

    def render(self, name, properties=None):
        if properties is None:
            properties = self.properties
        if properties is not None:
            for k, v in properties.items():
                if isinstance(v, OpenApiReference) and "{self}" in v.reference:
                    v.reference = v.reference.replace("{self}", name)
                    properties[k] = v
                elif type(v) in [dict]:
                    v = self.render(name, v)
                    properties[k] = v
        return properties

    def __iter__(self):
        yield 'type', self.data_type[0].value if len(self.data_type) == 1 else [v.value for v in self.data_type]

        # Find valid fields for our data type
        valid_fields = [OpenApiSchemaValidFieldsByType[t] for t in self.data_type]
        valid_fields = [y for x in valid_fields for y in x]
        for k, v in vars(self).items():
            if k not in ['data_type'] and k in valid_fields:
                if v is not None:
                    if type(v) in [list, dict]:
                        v = nested_convert(v)
                    elif isinstance(v, IgnoreNoneIterMixin):
                        v = dict(v)
                    if v not in [{}, []]:
                        yield self.remapped_fields[k] if k in self.remapped_fields else k, v


def nested_convert(data: Union[dict, list]):
    result = {} if type(data) is dict else []

    if type(data) is dict:
        for k, v in data.items():
            if type(v) in [dict, List]:
                nv = nested_convert(v)
                if nv not in [{}, []]:
                    result[k] = nv
            elif isinstance(v, IgnoreNoneIterMixin):
                result[k] = dict(v)

    else:
        for v in data:
            if type(v) in [dict, List]:
                result.append(nested_convert(v))
            elif isinstance(v, IgnoreNoneIterMixin):
                result.append(dict(v))
    return result


class OpenApiSchemaCombine:
    def __init__(self, combine_type: OpanApiSchemaCombineType,
                 schemas: List[Union[OpenApiReference, OpenApiSchema]]):
        self.combine_type = combine_type
        self.schemas = schemas

    def __iter__(self):
        yield self.combine_type.value, [dict(s) for s in self.schemas]


class OpenApiMediaType(IgnoreNoneIterMixin):

    def __init__(self, schema: Union[OpenApiSchema, OpenApiReference], example: Any = None,
                 examples: Dict[str, Union[OpenApiReference, OpenApiExample]] = None,
                 encoding: Dict[str, OpenApiEncoding] = None):
        """

        Args:
            schema: The schema defining the type used for the request body.
            example: Any	Example of the media type. The example object SHOULD be in the correct format as specified
                by the media type. The example object is mutually exclusive of the examples object. Furthermore, if
                referencing a schema which contains an example, the example value SHALL override the example provided
                 by the schema.
            examples: Examples of the media type. Each example object SHOULD match the media type and specified schema
                if present. The examples object is mutually exclusive of the example object. Furthermore,
                if referencing a schema which contains an example, the examples value SHALL override the example
                provided by the schema.
            encoding: A map between a property name and its encoding information. The key, being the property name,
                MUST exist in the schema as a property. The encoding object SHALL only apply to requestBody objects when
                the media type is multipart or application/x-www-form-urlencoded.

        See Also:
            https://github.com/OAI/OpenAPI-Specification/blob/master/versions/3.0.0.md#mediaTypeObject
        """
        self.schema = schema
        self.example = example
        self.examples = examples
        self.encoding = encoding


class OpenApiResponse(IgnoreNoneIterMixin):

    def __init__(self, description: str, headers: Dict[str, OpenApiHeader] = None,
                 content: Dict[str, OpenApiMediaType] = None,
                 links: Dict[str, Union[OpenApiLink, OpenApiReference]] = None):
        """

        Args:
            description: REQUIRED. A short description of the response. CommonMark syntax MAY be used for rich text representation.
            headers: Maps a header name to its definition. RFC7230 states header names are case insensitive. If a
                response header is defined with the name "Content-Type", it SHALL be ignored.
            content: A map containing descriptions of potential response payloads. The key is a media type or media
                type range and the value describes it. For responses that match multiple keys, only the most specific
                key is applicable. e.g. text/plain overrides text/*
            links: A map of operations links that can be followed from the response. The key of the map is a short name
                for the link, following the naming constraints of the names for Component Objects.

        See Also:
            - https://github.com/OAI/OpenAPI-Specification/blob/master/versions/3.0.0.md#responseObject
        """
        self.description = description
        self.headers = headers
        self.content = content
        self.links = links


OpenApiResponseOrReference = Union[OpenApiReference, OpenApiResponse]


class OpenApiResponses(IgnoreNoneIterMixin):

    def __init__(self, default: OpenApiResponseOrReference = None, status_codes: Dict[int, OpenApiResponse] = None):
        """

        Args:
            default: The documentation of responses other than the ones declared for specific HTTP response codes.
                Use this field to cover undeclared responses. A Reference Object can link to a response that the
                OpenAPI Object's components/responses section defines.
            status_codes: Any HTTP status code can be used as the property name, but only one property per code, to
                describe the expected response for that HTTP status code. A Reference Object can link to a response
                that is defined in the OpenAPI Object's components/responses section. This field MUST be enclosed in
                quotation marks (for example, "200") for compatibility between JSON and YAML. To define a range of
                response codes, this field MAY contain the uppercase wildcard character X. For example, 2XX represents
                all response codes between [200-299]. The following range definitions are allowed: 1XX, 2XX, 3XX, 4XX,
                 and 5XX. If a response range is defined using an explicit code, the explicit code definition takes
                 precedence over the range definition for that code.

        See Also:
            - https://github.com/OAI/OpenAPI-Specification/blob/master/versions/3.0.0.md#responses-object
        """
        self.default = default
        self.status_codes = status_codes

    def __iter__(self):
        if self.default:
            yield 'default', self.default

        if self.status_codes:
            for k, v in self.status_codes.items():
                yield k, dict(v)


class OpenApiRequestBody(IgnoreNoneIterMixin):

    def __init__(self, content: Dict[str, OpenApiMediaType], description: str = None, required: bool = False):
        """

        Args:
            content: REQUIRED. The content of the request body. The key is a media type or media type range and the
                value describes it. For requests that match multiple keys, only the most specific key is applicable.
                e.g. text/plain overrides text/*
            description: A brief description of the request body. This could contain examples of use. CommonMark
            syntax MAY be used for rich text representation.
            required: Determines if the request body is required in the request. Defaults to false.

        See Also:
            - https://github.com/OAI/OpenAPI-Specification/blob/master/versions/3.0.0.md#requestBodyObject
        """
        self.content = content
        self.description = description
        self.required = required


class OpenApiParameterInput(Enum):
    PATH = 'path'
    HEADER = 'header'
    COOKIE = 'cookie'
    QUERY = 'query'

    def __repr__(self):
        return self.value()


class OpenApiParameter(IgnoreNoneIterMixin):
    def __init__(self, input_from: OpenApiParameterInput, name: str, description: str = None, required: bool = False,
                 deprecated: bool = False, allow_empty: bool = False, style: str = None, explode: bool = False,
                 allow_reserved: bool = False, schema: Union[OpenApiReference, OpenApiSchema] = None,
                 example: Any = None, examples: Dict[str, Union[OpenApiExample, OpenApiReference]] = None):
        """

        Args:
            input_from: REQUIRED. The location of the parameter. Possible values are "query", "header", "path" or "cookie".
                name: REQUIRED. The name of the parameter. Parameter names are case sensitive.

                - If in is "path", the name field MUST correspond to the associated path segment from the path field in
                  the Paths Object. See Path Templating for further information.
                - If in is "header" and the name field is "Accept", "Content-Type" or "Authorization", the parameter
                  definition SHALL be ignored.
                - For all other cases, the name corresponds to the parameter name used by the in property.
            description: A brief description of the parameter. This could contain examples of use. CommonMark syntax
                MAY be used for rich text representation.
            required: Determines whether this parameter is mandatory. If the parameter location is "path", this
                property is REQUIRED and its value MUST be true. Otherwise, the property MAY be included and its
                default value is false.
            deprecated: Specifies that a parameter is deprecated and SHOULD be transitioned out of usage.
            allow_empty: Sets the ability to pass empty-valued parameters. This is valid only for query parameters and
                allows sending a parameter with an empty value. Default value is false. If style is used, and if
                behavior is n/a (cannot be serialized), the value of allowEmptyValue SHALL be ignored.
            examples (Dict[str, Union[OpenApiExample, OpenApiReference]]): Examples of the media type. Each
                example SHOULD contain a value in the correct format as specified in the parameter encoding.
                The examples object is mutually exclusive of the example object. Furthermore, if referencing a schema
                which contains an example, the examples value SHALL override the example provided by the schema.

        See Also:
            - https://github.com/OAI/OpenAPI-Specification/blob/master/versions/3.0.0.md#parameterObject
        """

        self.input_from = input_from
        self.name = name
        self.description = description
        self.required = required
        self.deprecated = deprecated
        self.allow_empty = allow_empty
        self.style = style
        self.explode = explode
        self.allow_reserved = allow_reserved
        self.schema = schema
        self.example = example
        self.examples = examples

    @property
    def remapped_fields(self):
        return dict(input_from='in', allow_empty='allowEmptyValue', allow_reserved='allowReserved')


class OpenApiCallback(IgnoreNoneIterMixin):
    def __init__(self, expressions: Dict[str, 'OpenApiPath'] = None):
        self.expressions = expressions

    def __iter__(self):
        for k, v in self.expressions.items():
            yield k, v


class OpenApiPathOperation(IgnoreNoneIterMixin):
    def __init__(self, responses: OpenApiResponses, tags: List[str] = None, summary: str = None,
                 description: str = None, external_docs: OpenApiExternalDocumentation = None, operation_id: str = None,
                 parameters: List[Union[OpenApiReference, OpenApiParameter]] = None,
                 request_body: Union[OpenApiReference, OpenApiRequestBody] = None,
                 callbacks: Dict[str, OpenApiCallback] = None, deprecated: bool = False,
                 security: List[OpenApiSecurity] = None, servers: List[OpenApiServer] = None):
        """

        Args:
            responses: REQUIRED. The list of possible responses as they are returned from executing this operation.
            tags: A list of tags for API documentation control. Tags can be used for logical grouping of operations by
                  resources or any other qualifier.
            summary: A short summary of what the operation does.
            description:  verbose explanation of the operation behavior. CommonMark syntax MAY be used for rich text
                representation.
            external_docs: Additional external documentation for this operation.
            operation_id: Unique string used to identify the operation. The id MUST be unique among all operations
                described in the API. Tools and libraries MAY use the operationId to uniquely identify an operation,
                therefore, it is RECOMMENDED to follow common programming naming conventions.
            parameters: A list of parameters that are applicable for this operation. If a parameter is already defined
                at the Path Item, the new definition will override it but can never remove it. The list MUST NOT
                include duplicated parameters. A unique parameter is defined by a combination of a name and location.
                The list can use the Reference Object to link to parameters that are defined at the OpenAPI Object's
                components/parameters.
            request_body: The request body applicable for this operation. The requestBody is only supported in HTTP
                methods where the HTTP 1.1 specification RFC7231 has explicitly defined semantics for request bodies.
                In other cases where the HTTP spec is vague, requestBody SHALL be ignored by consumers.
            callbacks: A map of possible out-of band callbacks related to the parent operation. The key is a unique
                identifier for the Callback Object. Each value in the map is a Callback Object that describes a request
                that may be initiated by the API provider and the expected responses. The key value used to identify
                the callback object is an expression, evaluated at runtime, that identifies a URL to use for the
                callback operation.
            deprecated: Declares this operation to be deprecated. Consumers SHOULD refrain from usage of the declared
                operation. Default value is false.
            security: A declaration of which security mechanisms can be used for this operation. The list of values
                includes alternative security requirement objects that can be used. Only one of the security
                requirement objects need to be satisfied to authorize a request. This definition overrides any
                declared top-level security. To remove a top-level security declaration, an empty array can be used.
            servers: An alternative server array to service this operation. If an alternative server object is
                specified at the Path Item Object or Root level, it will be overridden by this value.
        """
        self.responses = responses
        self.tags = tags if tags else []
        self.summary = summary
        self.description = description
        self.external_docs = external_docs
        self.operation_id = operation_id
        self.parameters = parameters if parameters else []
        self.request_body = request_body
        self.callbacks = callbacks
        self.security = security if security else []
        self.servers = servers if servers else []
        self.deprecated = deprecated

    @property
    def remapped_fields(self):
        return dict(operation_id='operationId', external_docs='externalDocs', request_body='requestBody')

    @property
    def required_fields(self):
        return ['responses']


class OpenApiMethod(Enum):
    GET = 'get'
    POST = 'post'
    PUT = 'put'
    DELETE = 'delete'
    OPTIONS = 'options'
    HEAD = 'head'
    PATCH = 'patch'
    TRACE = 'trace'

    def __repr__(self):
        return self.value()


class OpenApiComponents(IgnoreNoneIterMixin):
    def __init__(self, schemas: Dict[str, OpenApiSchema] = None, responses: Dict[str, OpenApiResponse] = None,
                 parameters: Dict[str, OpenApiParameter] = None, examples: Dict[str, OpenApiExample] = None,
                 request_bodies: Dict[str, OpenApiRequestBody] = None, headers: Dict[str, OpenApiHeader] = None,
                 security_schemes: Dict[str, OpenApiSecurity] = None, links: Dict[str, OpenApiLink] = None,
                 callbacks: Dict[str, OpenApiCallback] = None):
        """

        Args:
            schemas: An object to hold reusable Schema Objects.
            responses: An object to hold reusable Response Objects.
            parameters: An object to hold reusable Parameter Objects.
            examples: An object to hold reusable Example Objects.
            request_bodies: An object to hold reusable Request Body Objects.
            headers: An object to hold reusable Header Objects.
            security_schemas: An object to hold reusable Security Scheme Objects.
            links: An object to hold reusable Link Objects.
            callbacks: An object to hold reusable Callback Objects.

        See Also:
            - https://github.com/OAI/OpenAPI-Specification/blob/master/versions/3.0.0.md#components-object
        """
        self.schemas = schemas if schemas else {}
        self.responses = responses if responses else {}
        self.parameters = parameters if parameters else {}
        self.examples = examples if examples else {}
        self.request_bodies = request_bodies if request_bodies else {}
        self.headers = headers if headers else {}
        self.security_schemes = security_schemes if security_schemes else {}
        self.links = links if links else {}
        self.callbacks = callbacks if callbacks else {}

    @property
    def remapped_fields(self):
        return dict(security_schemes='securitySchemes', request_bodies='requestBodies')

    def __iter__(self):
        for k, v in self.schemas.items():
            v.render(k)
        for k, v in super().__iter__():
            yield k, v


class OpenApiPath(IgnoreNoneIterMixin):
    def __init__(self, operations: Dict[OpenApiMethod, OpenApiPathOperation] = None, reference: str = None,
                 summary: str = None, description: str = None, servers: List[OpenApiServer] = None,
                 parameters: List[OpenApiReference] = None):
        """

        Args:
            operations: A map of http methods to operations
            reference: Allows for an external definition of this path item. The referenced structure MUST be in the
            format of a Path Item Object. If there are conflicts between the referenced definition and this Path Item's definition, the behavior is undefined.
            summary: An optional, string summary, intended to apply to all operations in this path.
            description: 	An optional, string description, intended to apply to all operations in this path.
            CommonMark syntax MAY be used for rich text representation.
            servers: An alternative server array to service all operations in this path.
            parameters: A list of parameters that are applicable for all the operations described under this path.
            These parameters can be overridden at the operation level, but cannot be removed there. The list MUST NOT
             include duplicated parameters. A unique parameter is defined by a combination of a name and location. The
              list can use the Reference Object to link to parameters that are defined at the OpenAPI Object's
              components/parameters.

        See Also:
            - https://github.com/OAI/OpenAPI-Specification/blob/master/versions/3.0.0.md#pathItemObject
        """
        self.operations = operations if operations else {}
        self.description = description
        self.reference = reference
        self.summary = summary
        self.servers = servers
        self.parameters = parameters

    @property
    def remapped_fields(self):
        return dict(reference='$ref')

    def __iter__(self):
        for k, v in vars(self).items():
            if k == 'operations' and v:
                for meth, op in self.operations.items():
                    yield str(meth), dict(op)
            elif not k.startswith("___"):
                if v is not None:
                    fname = k if k not in self.remapped_fields else self.remapped_fields[k]
                    yield fname, v


class OpenApiPaths(IgnoreNoneIterMixin):
    def __init__(self, paths: Dict[str, OpenApiPath] = None):
        self.paths = paths if paths else {}

    def __iter__(self):
        for k, v in self.paths.items():
            yield k, dict(v)


class OpenApiDocument(IgnoreNoneIterMixin):
    def __init__(self, info: OpenApiInfo, paths: OpenApiPaths, version: str = '3.0.0',
                 servers: List[OpenApiServer] = None, components: OpenApiComponents = None,
                 security: List[OpenApiSecurity] = None, tags: List[OpenApiTag] = None,
                 external_docs: OpenApiExternalDocumentation = None):
        """

        Args:
            info: REQUIRED. Provides metadata about the API. The metadata MAY be used by tooling as required.
            paths: REQUIRED. The available paths and operations for the API.
            version: This string MUST be the semantic version number of the OpenAPI Specification version that the
            OpenAPI document uses. Defaults to 3.0.0
            servers: 	An array of Server Objects, which provide connectivity information to a target server. If the
            servers property is not provided, or is an empty array, the default value would be a Server Object with a url value of /.
            components: An element to hold various schemas for the specification.
            security: A declaration of which security mechanisms can be used across the API. The list of values includes alternative security requirement objects that can be used. Only one of the security requirement objects need to be satisfied to authorize a request. Individual operations can override this definition.
            tags: A list of tags used by the specification with additional metadata. The order of the tags can be used to reflect on their order by the parsing tools. Not all tags that are used by the Operation Object must be declared. The tags that are not declared MAY be organized randomly or based on the tools' logic. Each tag name in the list MUST be unique.
            external_docs: Additional external documentation.

        See Also:
            https://github.com/OAI/OpenAPI-Specification/blob/master/versions/3.0.0.md#infoObject
        """
        self.openapi: str = version
        self.info: OpenApiInfo = info
        self.paths: OpenApiPaths = paths
        self.servers: List[OpenApiServer] = servers if servers else []
        self.components: OpenApiComponents = components
        self.security: List[OpenApiSecurity] = security if security else []
        self.tags: List[OpenApiTag] = tags if tags else []
        self.external_docs: OpenApiExternalDocumentation = external_docs

    @property
    def remapped_fields(self):
        return dict(external_docs='externalDocs')

    @property
    def required_fields(self):
        return ['openapi', 'info', 'paths']
