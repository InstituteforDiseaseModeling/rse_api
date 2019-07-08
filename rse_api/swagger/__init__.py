from rse_api.swagger.swagger_registry import get_swagger_registry


def register_swagger(app):
    """
    Add register swagger to load controller and call swagger json at start of app

    Args:
        app:

    Returns:

    """
    from .swagger_controller import get_swagger_json

    @app.before_first_request
    def initialize_swagger():
        get_swagger_json()


from .import swagger_spec, decorators
__all__ = ['swagger_spec', 'decorators']