from flask import Blueprint, request, session, render_template, redirect, \
    url_for, flash

from ..utils.db import db_conn

# create main frontend blueprint
auth = Blueprint(
    "auth",
    __name__,
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

    # if already logged in, redirect to index page
    if "id" in session:
        return redirect(url_for("frontend.index"))

    # if get, render login page
    if request.method == "GET":
        return render_template("login.html")

    # if post, authenticate user
    elif request.method == "POST":

        # get form data
        username = request.form["username"]
        password = request.form["password"]
        print("Creds: ", username, password)

        # check database for user
        user = db_conn.db["users"].find_one({"username": username})
        print("User: ", user)

        # TODO: password checking goes here
        password = password  # shut up flask8

        # if no user, error and return
        if user is None:
            flash("Invalid username or password", "error")
            return redirect(url_for("auth.login"))

        # if user is not approved yet
        if user["approved"] is False:
            flash(
                "Your account has not yet been approved! Please \
                contact an admin if you believe this is an error.",
                "error",
            )
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

    # if not logged in, redirect to login page
    if "id" not in session:
        return redirect(url_for("auth.login"))

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


@auth.route("/signup", methods=["GET", "POST"])
def signup():
    """
    If GET, Renders the page where a user can sign up.
    IF POST, Registers the user and redirects to the login page.

    TODO: Sanitize form input
    """

    # if get, render login page
    if request.method == "GET":
        return render_template("signup.html")

    # if post, authenticate user
    elif request.method == "POST":

        # get form data
        # NOTE: role input is a bodge rn till frontend gets updated
        fname = request.form["firstname"]
        lame = request.form["lastname"]
        uname = request.form["username"]
        email = request.form["email"]
        passwd = request.form["password"]
        role = request.form["role"]

        # check database for user
        user = db_conn.db["users"].find_one({"username": uname})
        if user:
            flash("Username already in use!", "error")
            return redirect(url_for("auth.signup"))

        user = db_conn.db["users"].find_one({"email": email})
        if user:
            flash("Email already in use!", "error")
            return redirect(url_for("auth.signup"))

        # insert user into database
        auto_approve_users = True  # For later... ;) -A
        db_conn.db["users"].insert_one(
            {
                "firstname": fname,
                "lastname": lame,
                "username": uname,
                "email": email,
                "password": passwd,
                "role": int(role),
                "approved": auto_approve_users,
            }
        )

        # redirect
        if auto_approve_users:
            flash("Account created! You may now log in!", "info")
            return redirect(url_for("auth.login"))
        else:
            flash(
                "Account created! An admin will approve your account soon.",
                "info",
            )
            return redirect(url_for("auth.login"))
