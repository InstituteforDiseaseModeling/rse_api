import time
import unittest

from flask import Response, jsonify
from marshmallow import Schema, validate
from marshmallow.fields import Integer, String

from rse_api import get_application
from rse_api.decorators import (
    json_only,
    schema_in,
    schema_in_out,
    schema_out,
    singleton_function,
)
from tests.utils import requires_fixture


class PersonSchema(Schema):
    name = String(required=True, validate=validate.Length(min=5))
    age = Integer(missing=30)


class NameOnlySchema(Schema):
    name = String(required=True, validate=validate.Length(min=5))


class TestDecorator(unittest.TestCase):
    def test_singleton_function(self):
        @singleton_function
        def one_time():
            return time.time()

        def changes_time():
            return time.time()

        x = one_time()
        time.sleep(0.02)
        x2 = changes_time()
        time.sleep(0.02)
        x3 = one_time()
        time.sleep(0.02)
        x4 = changes_time()
        self.assertNotEqual(x, x2)
        self.assertNotEqual(x2, x3)
        self.assertNotEqual(x3, x4)
        self.assertNotEqual(x2, x4)
        self.assertEqual(x, x3)

    @requires_fixture("person")
    def test_schema_in(self, person):
        app = get_application()

        @app.route("/test_schema_in", methods=["POST"])
        @schema_in(PersonSchema())
        def schema_in_only_data_arg(data):
            self.assertEqual(data["name"], person["name"])
            return jsonify(data)

        client = app.test_client()

        result: Response = client.post(
            "/test_schema_in",
            data=PersonSchema().dumps(person).data,
            content_type="application/json",
        )

        self.assertEqual(result.status_code, 200)

    @requires_fixture("person")
    def test_json_only(self, person):
        app = get_application()

        del person["name"]

        @app.route("/test_json_only", methods=["POST"])
        @json_only
        def schema_json_only(data):
            self.assertEqual(data["name"], person["name"])
            return jsonify(data)

        client = app.test_client()

        result: Response = client.post(
            "/test_json_only", data=PersonSchema().dumps(person).data
        )

        self.assertEqual(result.status_code, 400)
        message = result.json
        self.assertIn("message", message)
        self.assertIn("Only JSON Requests are accepted", message["message"])

    @requires_fixture("person")
    def test_schema_in_strict(self, person):
        app = get_application()

        del person["name"]

        @app.route("/test_schema_in_strict", methods=["POST"])
        @schema_in(PersonSchema(strict=True))
        def schema_strict(data):
            self.assertEqual(data["name"], person["name"])
            return jsonify(data)

        client = app.test_client()

        result: Response = client.post(
            "/test_schema_in_strict",
            data=PersonSchema().dumps(person).data,
            content_type="application/json",
        )

        self.assertEqual(result.status_code, 400)
        message = result.json
        self.assertIn("messages", message)
        self.assertIn("name", message["messages"])

    @requires_fixture("person")
    def test_schema_out(self, person):
        app = get_application()

        @app.route("/test_schema_out", methods=["GET"])
        @schema_out(PersonSchema())
        def schema_out_fn():
            return person

        client = app.test_client()

        result: Response = client.get(
            "/test_schema_out", content_type="application/json"
        )
        self.assertEqual(result.status_code, 200)
        data = result.json
        for k, v in data.items():
            self.assertEqual(person[k], v)

    @requires_fixture("person")
    def test_schema_in_out(self, person):
        app = get_application()

        @app.route("/test_schema_in_out", methods=["POST"])
        @schema_in_out(PersonSchema(), NameOnlySchema())
        def schema_in_out_fn(data):
            data["name"] = data["name"].replace(" ", "_")
            return data

        client = app.test_client()

        result: Response = client.post(
            "/test_schema_in_out",
            data=PersonSchema().dumps(person).data,
            content_type="application/json",
        )
        data = result.json
        self.assertEqual(result.status_code, 200)
        self.assertEqual(list(data.keys()), ["name"])
        for k, v in data.items():
            self.assertEqual(person[k].replace(" ", "_"), v)
