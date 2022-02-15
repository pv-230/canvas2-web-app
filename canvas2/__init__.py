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
          - Add input validation
        """
        return render_template('login.html')

    @app.route("/authenticate", methods=["POST"])
    def authenticate():
        """
        Authenticates the user based on the provided credentials.
        This is just a placeholder for now.
        """

        return redirect(url_for("index"))

    @app.route("/signup")
    def signup():
        """
        Renders the page where a user can create a new account.

        TODO:
          - Add a check to see if already logged in and redirect to home if so
        """

        return render_template('signup.html')

    @app.route("/create-account")
    def createAccount():
        """
        Creates a new account in the database for the user.
        This is just a placeholder for now.
        """

        redirect(url_for("index"))

    # return the app
    return app
