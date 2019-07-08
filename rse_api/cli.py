import click
from flask import Flask
from flask.cli import AppGroup


def show_routes(app:Flask = None):
    """
    Utility function that will print out all the urls defined in the current application

    Args:
        app: Optional flask app to show routes for. If none is specified, None is returned

    Returns:
        None
    """
    if app is None:
        from flask import current_app
        app = current_app
    for rule in app.url_map.iter_rules():

        options = {}
        for arg in rule.arguments:
            options[arg] = "[{0}]".format(arg)

        methods = ','.join(rule.methods)
        url = str(rule)
        line = "{:50s} {:20s} {}".format(rule.endpoint, methods, url)
        app.logger.info(line)


def add_cli(app: Flask) -> AppGroup:
    """
    Defines the manage cli commands

    Args:
        app: Flask app to add cli too

    Returns:
        Returns manage cli group
    """
    manage_cli = AppGroup('manage', help="Commands related to running application")

    @manage_cli.command('run', help='Runs the application')
    @click.option('--host', default='127.0.0.1', help='What Host should the app run on')
    @click.option('--port', default=5000, help='What port should the server run on?')
    def run(host, port):
        if app.env in ['dev', 'development', 'test', 'testing']:
            show_routes()
        app.run(host=host, port=port)

    app.cli.add_command(manage_cli)
    return manage_cli
