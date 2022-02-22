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

        return "<p>Hello, World!</p>"

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
        # the login fails. Enter "test" as the username or password to fail the
        # login.
        if (username == "test" or password == "test"):
            flash("Invalid username or password", "error")
            return redirect(url_for("login"))
        else:
            return redirect(url_for("index"))

    @app.route("/signup")
    def signup():
        """Renders the page where a user can create a new account."""

        return render_template("signup.html")

    @app.route("/create-account", methods=["POST"])
    def createAccount():
        """Creates a new account in the database for the user.

        TODO: More secure method of sending password from client-side
        TODO: Need function that verifies form input
        TODO: Sanitize input.
        """

        # firstname = request.form["firstname"]
        # lastname = request.form["lastname"]
        username = request.form["username"]
        email = request.form["email"]
        # password = request.form["password"]
        # passwordConfirm = request.form["password-confirm"]
        isTeacher = request.form.get("is-teacher")

        # Placeholders to test signup failure
        success = True
        if (username == "test"):
            success = False
            flash("Username already in use", "error")
        if (email == "test@test"):
            success = False
            flash("Email already in use", "error")

        if(success and isTeacher == "on"):
            flash("Account creation pending approval", "info")
            return redirect(url_for("login"))
        elif (success):
            flash("Account creation successful", "info")
            return redirect(url_for("login"))
        else:
            return redirect(url_for("signup"))

    # return the app
    return app
