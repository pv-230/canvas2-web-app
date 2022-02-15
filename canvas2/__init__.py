from flask import Flask, render_template, redirect, url_for


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
    def index():
        return "<h1>Under construction</<h1>"

    @app.route("/login")
    def login():
        """
        Renders the page where a user can login.

        TODO:
          - Add a check to see if already logged in and redirect to home if so
        """
        return render_template('login.html')

    @app.route("/authenticate", methods=["POST"])
    def authenticate():
        """
        Authenticates the user based on the provided credentials.

        TODO:
          - Implement this part in a secure fashion, currently just here for
            as a placeholder
        """

        return redirect(url_for("index"))

    # return the app
    return app
