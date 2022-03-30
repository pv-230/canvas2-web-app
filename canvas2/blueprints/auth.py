from flask import Blueprint, request, session, render_template, redirect, url_for, \
    flash, jsonify

from ..utils.db import db_conn

# create main frontend blueprint
auth = Blueprint(
    'auth', __name__,
    url_prefix="/auth",
)


@auth.route("/login", methods=["GET", "POST"])
def login():
    """
    If GET, Renders the page where a user can login.
    IF POST, Authenticates the user and redirects to the index page.

    TODO: Need function that verifies username/password
      NOTE: Done! At least partially. -A
    TODO: Sanitize form input
    """

    # if get, render login page
    if request.method == "GET":
        return render_template("login.html")

    # if post, authenticate user
    elif request.method == "POST":

        # if already logged in, redirect to index page
        if "id" in session:
            return redirect(url_for("frontend.index"))

        # get form data
        username = request.form["username"]
        password = request.form["password"]

        # check database for user
        user = db_conn.db.users.find_one({"username": username})

        # TODO: password checking goes here
        password = password  # shut up flask8

        # if no user, error and return
        if user is None:
            flash("Invalid username or password", "error")
            return redirect(url_for("auth.login"))

        # else, save vars to session and redirect to home
        session["id"] = str(user["_id"])
        session["username"] = user["username"]
        session["fname"] = user["firstname"]
        session["lname"] = user["lastname"]
        session["role"] = user["role"]

        return redirect(url_for("frontend.index"))

@auth.route("/logout", methods=["GET"])
def logout():
    """Logs out the user and redirects to the login page."""

    # clear session variables
    del session["id"]
    del session["username"]
    del session["fname"]
    del session["lname"]
    del session["role"]

    # flash message
    flash("You have been logged out.", "info")

    # redirect
    return redirect(url_for("auth.login"))
