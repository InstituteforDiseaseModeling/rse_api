
import click
from flask.cli import AppGroup


def add_cli(app):
    manage_cli = AppGroup('manage', help="Commands related to running application")
    
    @manage_cli.command('run', help='Runs the application')
    @click.option('--port', default=5000, help='What port should the server run on?')
    def run(port):
        app.run(port=port)

    app.cli.add_command(manage_cli)
    