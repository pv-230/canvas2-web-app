import os
from urllib.request import urlopen

from flask import Flask, g

from flask_pymongo import PyMongo
from pymongo.errors import ServerSelectionTimeoutError

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

    # get app context for mongodb connection
    with app.app_context():

        # make sure we have a conn string
        if not os.environ.get("MONGO_URI"):
            print("ERROR: MONGO_URI is not set!")
            exit(-1)

        # init mongodb connection and save it in global state
        # start by creating our client with a connection timeout of 3 seconds
        app.config["MONGO_URI"] = os.environ.get("MONGO_URI")
        g.mongo = PyMongo(app, serverSelectionTimeoutMS=3000)

        # now, test the connection
        # is not whitelisted, this will throw ServerSelectionTimeoutError
        # on fail, print verbose error to help other devs understand what's up
        try:
            g.mongo.cx.server_info()
        except ServerSelectionTimeoutError:
            external_ip = urlopen('https://v4.ident.me').read().decode('utf8')
            print("ERROR: Could not connect to Mongo! Please ensure that your IP is whitelisted on Atlas!")
            print(f"Your current IP: {external_ip}")
            exit(-1)

    # import blueprints
    from .blueprints import frontend

    # register frontend
    app.register_blueprint(
        frontend
    )

    # return the app
    return app
