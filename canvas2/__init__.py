from flask import Flask, render_template, redirect, url_for, flash, request


def create_app(config=None):

    # initialize application
    app = Flask(__name__)

    # TODO: Change this to something else later
    app.secret_key = "i_need_a_key_to_flash_messages_without_errors"

    # initialize config, if it exists
    # in most cases our config is automatically loaded from .flaskenv, but
    # for testing we're programatically required to set TESTING to True
    if config:
        app.config.update(config)

    @app.route("/")
    def index():
        "Renders the homepage"

        return "<h1>Under construction</<h1>"

    @app.route("/login")
    def login():
        """Renders the page where a user can login."""

        return render_template("login.html")

    @app.route("/authenticate", methods=["POST"])
    def authenticate():
        """Authenticates the user based on the provided credentials.

        TODO: More secure method of sending password from client-side
        TODO: Need function that verifies username/password
        TODO: Sanitize form input
        """

        # Form data
        username = request.form["username"]
        password = request.form["password"]

        # The condition is just a placeholder now to test what happens when
        # the login fails. Enter "test" as the username/password to fail the
        # login.
        if (username != "test" and password != "test"):
            return redirect(url_for("index"))
        else:
            flash("Invalid username or password", "error")
            return redirect(url_for("login"))

    @app.route("/signup")
    def signup():
        """Renders the page where a user can create a new account."""

        return render_template("signup.html")

    @app.route("/create-account", methods=["POST"])
    def createAccount():
        """Creates a new account in the database for the user.

        TODO: Sanitize input.
        """

        redirect(url_for("index"))

    # return the app
    return app
