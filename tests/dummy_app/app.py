import os
from rse_api import get_application
from rse_api.utils import load_modules

APP_NAME = 'tests.dummy_app'
SETTING_OBJECT = f"{APP_NAME}.default_settings"

# Initialize our Flask application. We provide the path to our default settings object
application = get_application(SETTING_OBJECT)

current_dir = os.path.dirname( os.path.realpath(__file__))

# setup controllers
load_modules(f"{APP_NAME}.controllers", os.path.join(current_dir, 'controllers'))
load_modules(f"{APP_NAME}.tasks", os.path.join(current_dir, 'tasks'))

# Run the cli and let the parameters determine what we
# To run, run python app.py manage run
# or to setup db run
# python app.py db create
if __name__ == "__main__":
    application.cli()