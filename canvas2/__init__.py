import os
from flask import Flask
from dotenv import load_dotenv
from .utils.db import init_db

def create_app(config=None):

    # initialize application
    app = Flask(__name__)

    # TODO: Change this to something else later
    app.secret_key = os.environ.get("SECRET_KEY")

    # initialize config, if it was passed in via testing suite
    # in most cases our config is automatically loaded from .flaskenv, but
    # for testing we're programatically required to set TESTING to True
    if config:
        app.config.update(config)

    # init db
    init_db(app)

    # import blueprints
    from .blueprints import frontend, backend, auth
    app.register_blueprint(frontend)
    app.register_blueprint(backend)
    app.register_blueprint(auth)

    # return the app
    return app
