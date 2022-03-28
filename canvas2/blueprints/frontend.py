from flask import Blueprint, request, g, render_template, redirect, url_for, \
    flash, jsonify

# These are a bunch of testing variables that should be removed once we get
# the databased hooked up.
courses = []
courses.append(
    {
        "title": "Object Oriented Programming",
        "code": "COP3330",
        "description": "Learn some OOP.",
        "assignments": [],
        "users": [
            {
                "name": "OOP Instructor",
                "role": "teacher"
            }
        ],
    }
)
courses.append(
    {
        "title": "Computer Organization I",
        "code": "CDA3100",
        "description": "Learn some computer organization.",
        "assignments": [],
        "users": [
            {
                "name": "Comp Org Instructor",
                "role": "teacher"
            }
        ],
    }
)
courses.append(
    {
        "title": "Secure, Parallel, and Distributed Computing with Python",
        "code": "COP4521",
        "description": "Learn some secure, parallel, and distributed stuff.",
        "assignments": [
            {
                "title": "Assignment 1",
                "description": "This is the first assignment.",
                "dueDate": "03/22/2022",
                "dueTime": "11:59PM",
                "isSubmitted": False,
            }
        ],
        "users": [
            {"name": "SPD Instructor", "role": "teacher"},
            {"name": "Juan Smith", "role": "ta"},
            {"name": "John Smith", "role": "student"},
            {"name": "Bob Smith", "role": "student"},
        ],
    }
)
role = "teacher"
isLoggedIn = True

# initialize frontend blueprint
frontend = Blueprint(
    'frontend', __name__,
    template_folder='templates'
)


@frontend.route("/")
def index():
    """Renders the homepage

    TODO: Need way of telling if user is logged in
        - NOTE: you can use flask.session for this :) -A
    TODO: Need to determine if user is a teacher
    TODO: Need to obtain list of classes user is associated with
    """

    if isLoggedIn:
        return render_template("home.html", role=role, courses=courses)
    else:
        return redirect(url_for("login"))


@frontend.route("/<code>")
def course_page(code):
    """Renders the appropriate course page for a user.

    TODO: Add a way to determine if user is enrolled in the course
            specified by the code in the URL
    """

    # Replace this with a database function that looks up if the course
    # code is found in the user's enrollments
    for course in courses:
        if course["code"] == code:
            return render_template("course.html", role=role, course=course)

    return redirect(url_for("index"))


@frontend.route("/login")
def login():
    """Renders the page where a user can login."""

    return render_template("login.html")


@frontend.route("/authenticate", methods=["POST"])
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
    if username == "test" or password == "test":
        flash("Invalid username or password", "error")
        return redirect(url_for("login"))
    else:
        return redirect(url_for("index"))


@frontend.route("/signup")
def signup():
    """Renders the page where a user can create a new account."""

    return render_template("signup.html")


@frontend.route("/create-account", methods=["POST"])
def create_account():
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
    if username == "test":
        success = False
        flash("Username already in use", "error")
    if email == "test@test":
        success = False
        flash("Email already in use", "error")

    if success and isTeacher == "on":
        flash("Account creation pending approval", "info")
        return redirect(url_for("login"))
    elif success:
        flash("Account creation successful", "info")
        return redirect(url_for("login"))
    else:
        return redirect(url_for("signup"))


@frontend.route("/add-course", methods=["POST"])
def add_course():
    """Adds a course to the database.

    TODO: Need to add functionality here to add a course into the database
    TODO: Add more form data as needed, going with bare minimum for now
    """
    # courseName = request.form["course-name"]
    return redirect(url_for("index"))


@frontend.route("/submit-assignment", methods=["POST"])
def submit_assignment():
    """Submits an assignment to the database.

    TODO: Need to add a function here to save a student's submission to db
    """

    courseCode = request.form["course-code"]
    return redirect(courseCode)


@frontend.route("/add-assignment", methods=["POST"])
def add_assignment():
    """Adds an assignment to the database.

    TODO: Need to add functionality here to add an assignment into the db
    """

    courseCode = request.form["course-code"]
    return redirect(courseCode)


@frontend.route("/change-roles", methods=["POST"])
def change_roles():
    """Changes the roles of users based on the list of role requests

    TODO: Add function to change a user's role
    """

    # roleRequests = request.get_json()
    # roleRequests is a JSON in the form of:
    #   {'userID': 'roleToBecome', ...}
    # print(roleRequests, flush=True)

    # Change this to a function that actually does the role swap in the db
    roleChangeSuccessful = True
    if roleChangeSuccessful:
        return jsonify(success=True), 200
    else:
        return jsonify(success=False), 418
