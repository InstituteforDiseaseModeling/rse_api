import sqlalchemy
from typing import List, Union
from flask import request, jsonify
from flask.views import MethodView

from rse_db.utils import get_db
from rse_api.query import get_pagination_from_request
from rse_api.decorators import json_only
from rse_api.errors import RSEApiException


class SimpleController(MethodView):
    def __init__(self, model, many_schema, single_schema=None,
                 exclude_on_post: List[str] = ['id'],
                 order_by: Union[str, sqlalchemy.Column] = 'id'):
        """
        Provides a controller to do basic crud operations

        :param model: SqlAlchemy to operate on. This should have the query Metaproperty setup
        :param many_schema: Marshmallow schema class that represent the List view of the model.
        Sometimes you may want to disable nested objects in the list view but most of the time
        there is one schema for both single and many
        :param single_schema: Schema for display of single objects and also for input.
        If not specified, the many schema will be used
        :param exclude_on_post: Fields to exclude on post
        :param order_by: Field to order list by default
        """
        super().__init__()
        # We assume that DB has been loaded before any controllers. Otherwise, some
        # application specific setup could be missed
        self.db = get_db()
        self.model = model
        self.many_schema = many_schema
        self.single_schema = single_schema if single_schema else self.many_schema
        self.exclude_on_post = exclude_on_post
        self.order_by = order_by

    def find_all(self):
        result = self.model.query.order_by(self.order_by).paginate(**get_pagination_from_request())
        resp = jsonify(self.many_schema().dump(result.items, many=True).data)
        resp.headers['X-Total-Pages'] = result.pages
        resp.headers['X-Current-Page'] = result.page
        resp.headers['X-Per-Pages'] = result.per_page
        resp.headers['X-Total'] = result.total
        return resp

    def find_one(self, id):
        return self.model.query.filter(self.model.id == id).one()

    def get(self, id):
        return self.find_all() if id is None else jsonify(
            self.single_schema().dump(self.find_one(id), many=False).data)

    @json_only
    def put(self, id):
        if id is None:
            raise RSEApiException("You must specify an id")

        result = self.single_schema(strict=True).load(request.json,
                                                      instance=self.find_one(id),
                                                      session=self.db.session,
                                                      partial=True)
        session = self.db.object_session(result.data)
        session.add(result.data)
        session.commit()
        return jsonify(self.single_schema().dump(result.data, many=False).data)

    @json_only
    def post(self, id=None):
        # check if we have a version
        sch = self.single_schema(strict=True, exclude=self.exclude_on_post, session=self.db.session)
        result = sch.load(request.json, session=self.db.session)
        session = self.db.session
        session.add(result.data)
        session.commit()
        return jsonify(self.single_schema().dump(result.data, many=False).data)

    def delete(self, id):
        if id is None:
            raise RSEApiException("You must specify an id")
        result = self.single_schema(strict=True).load({}, instance=self.find_one(id),
                                                      session=self.db.session,
                                                      partial=True)
        if result is None:
            raise FileNotFoundError("Cannot Find item with id {}".format(id))
        session = self.db.object_session(result.data)
        session.delete(result.data)
        session.commit()
        return '', 204
