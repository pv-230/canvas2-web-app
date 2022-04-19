import os
from flask import Flask
from .utils.db import init_db


def create_app(test_config=None):

    # initialize application
    app = Flask(__name__)

    # initial environment config
    app.secret_key = os.environ.get("SECRET_KEY")
    app.config["MONGO_URI"] = os.environ.get("MONGO_URI")

    # handle testing config, if it was passed in
    # we call this second because we want to overwite MONGO_URI
    # see: conftest.py:pytest_configure()
    if test_config:
        app.config.update(**test_config)

    # init db
    init_db(app)

    # import blueprints
    from .blueprints import frontend, backend, auth, admin
    app.register_blueprint(frontend)
    app.register_blueprint(backend)
    app.register_blueprint(auth)
    app.register_blueprint(admin)

    # return the app
    return app
