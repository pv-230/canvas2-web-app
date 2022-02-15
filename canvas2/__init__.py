from flask import Flask, render_template


def create_app(config=None):

    # initialize application
    app = Flask(__name__)

    # initialize config, if it exists
    # in most cases our config is automatically loaded from .flaskenv, but
    # for testing we're programatically required to set TESTING to True
    if config:
        app.config.update(config)

    # register endpoints
    @app.route("/")
    def hello_world():
        return "<p>Hello, World!</p>"

    @app.route("/login")
    def login():
        return render_template('login.html')

    # return the app
    return app
