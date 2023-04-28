from flask_restful import Api, Resource
from marshmallow import ValidationError, fields, validate, validates_schema
from marshmallow_sqlalchemy import ModelSchema
from rse_db.utils import get_declarative_base
from sqlalchemy import Column, Integer, String

from rse_api.decorators import register_resource, schema_in_out, schema_out

Base = get_declarative_base()


# Our Database Model
# This model handles all our interaction with DB
class ParameterModel(Base):
    id = Column(Integer(), primary_key=True, autoincrement=True)
    name = Column(String(255))
    min = Column(Integer())
    max = Column(Integer())

    @staticmethod
    def find_one(id):
        pass

    @staticmethod
    def save(data, session=None):
        # do any special data validations
        # manipulations or whatever
        # then save
        if session is None:
            session = ParameterModel.query.session
        instance = ParameterModel(**data)
        session.add(instance)
        session.commit()


# Schema for handling serialization and data validation on inputs
class ParameterSchema(ModelSchema):
    id = fields.Integer(required=True)
    name = fields.String(required=True)
    min = fields.Integer(validate=validate.Range(1, 4))
    max = fields.Integer(validate=validate.Range(1, 4))

    @validates_schema
    def check_min_less_than_max(self, data):
        if data["min"] >= data["max"]:
            message = "The Max must be larger than the min"
            raise ValidationError({"min": message, "max": message})

    class Meta:
        model = ParameterModel


# Resource to handle HTTP interactions
@register_resource("/parameters")
class Parameters(Resource):
    @schema_out(ParameterSchema())
    def get(self, id):
        return ParameterModel.find_one(id)

    @schema_in_out(ParameterSchema(exclude=["id"]), ParameterSchema())
    def post(self, data):
        return ParameterModel.save(data)

    @schema_in_out(ParameterSchema(), ParameterSchema())
    def put(self, data):
        data = ParameterSchema(strict=True).load(
            data,
            instance=ParameterModel.find_one(id),
            session=ParameterModel.query.session,
            partial=True,
        )
        ParameterModel.query.session.add(data)
        ParameterModel.query.session.commit()
