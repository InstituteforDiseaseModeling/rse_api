import os

TRUE_OPTIONS = ["true", "1", "y", "yes", "on"]

# make sure DEBUG is off unless enabled explicitly otherwise
DEBUG = os.environ.get("DEBUG", "False").lower() in TRUE_OPTIONS or os.environ.get("FLASK_ENV",
                                                                                   "production") == "development"
LOG_DIR = '.'  # create log files in current working directory
SQLALCHEMY_TRACK_MODIFICATIONS = os.environ.get("SQLALCHEMY_DATABASE_URI", "False").lower() in TRUE_OPTIONS
SQLALCHEMY_DATABASE_URI = os.environ.get("SQLALCHEMY_DATABASE_URI", 'sqlite:////tmp/test.db')
SQLALCHEMY_ECHO = os.environ.get("SQLALCHEMY_ECHO", DEBUG)
FLASK_ENV = os.environ.get('FLASK_ENV', 'testing')
