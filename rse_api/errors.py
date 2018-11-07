import importlib

from flask import jsonify


class RSEApiException(Exception):
    pass


def register_common_error_handlers(app):
    """
    Define the common error handlers

    If sqlalchemy exists, error capturing for IntegrityError and NoResultFound will be defined

    If marshmallow exists, error capturing for ValidationError will be defined
    :param app:
    :return: None
    """
    if importlib.find_loader('sqlalchemy'):
        app.logger.debug('Registering sqlalchemy error handlers')
        from sqlalchemy.exc import IntegrityError
        from sqlalchemy.orm.exc import NoResultFound

        @app.errorhandler(IntegrityError)
        def unhandled_exception(e):
            app.logger.exception(e)
            err_msg = str(e.orig)
            message = 'Save Failed due to IntegrityError, most likely due to a missing relationship. See {}'.format(str(e.orig))
            if 'UNIQUE constraint failed: configuration_parameters.key_string, ' in err_msg:
                message = "The Key String, Parameter, and Release Version must be Unique!"

            return jsonify({'message': message}), 400

        @app.errorhandler(NoResultFound)
        def unhandled_exception(e):
            app.logger.exception(e)
            return jsonify({'message': 'Cannot find the requested resource'}), 404

    if importlib.find_loader('marshmallow'):
        app.logger.debug('Registering marshmallow error handlers')
        from marshmallow import ValidationError

        @app.errorhandler(ValidationError)
        def unhandled_exception(e):
            app.logger.exception(e)
            if isinstance(e.messages, list) and len(e.field_names) > 0:
                e.messages = {field: e.messages for field in e.field_names}
            return jsonify({'messages': e.messages}), 400

    @app.errorhandler(RSEApiException)
    def rse_api_exceptionn(e):
        app.logger.exception(e)
        if isinstance(e.args, tuple):
            e.message = ' '.join(e.args)
        return jsonify({'message': e.message}), 400
