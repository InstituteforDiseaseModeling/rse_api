from importlib import util
from flask import jsonify, Flask


class RSEApiException(Exception):
    """
    Generic API Exception. We do this just to be able to track certain error types

    """
    pass


def register_common_error_handlers(app: Flask):
    """
    Registers a common set of error handlers including:
    - NoResultFound will be registered as a 404 error
    - Validation Errors will be registered as a 400
    - RSEApiException will be registered as 400s

    Args:
        app: Flask app to add errors to

    Returns:
        None
    """

    if util.find_spec('sqlalchemy'):
        app.logger.debug('Registering sqlalchemy error handlers')
        from sqlalchemy.orm.exc import NoResultFound

        @app.errorhandler(NoResultFound)
        def handle_no_result_exception(e):
            app.logger.exception(e)
            return jsonify({'message': 'Cannot find the requested resource'}), 404

    if util.find_spec('marshmallow'):
        app.logger.debug('Registering marshmallow error handlers')
        from marshmallow import ValidationError

        @app.errorhandler(ValidationError)
        def handle_validation_error(e):
            app.logger.exception(e)
            if isinstance(e.messages, list) and len(e.field_names) > 0:
                e.messages = {field: e.messages for field in e.field_names}
            return jsonify({'messages': e.messages}), 400

    @app.errorhandler(RSEApiException)
    def rse_api_exception(e):
        app.logger.exception(e)
        if isinstance(e.args, tuple):
            e.message = ' '.join(e.args)
        return jsonify({'message': e.message}), 400
