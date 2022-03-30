from bson import ObjectId
from flask import Blueprint, request, session, render_template, redirect, \
    url_for, flash, jsonify, abort

from ..utils.db import db_conn


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
isLoggedIn = False

# create main frontend blueprint
frontend = Blueprint(
    'frontend', __name__,
    template_folder='templates',
)


@frontend.route("/")
def index():
    """Renders the homepage

    TODO: Need way of telling if user is logged in
        - NOTE: you can use flask.session for this :) -A
    TODO: Need to determine if user is a teacher
    TODO: Need to obtain list of classes user is associated with
    """

    # if not logged in, send to login
    if "id" not in session:
        return redirect(url_for("auth.login"))

    # else, render home page
    else:

        # get all classes by user id
        courses = db_conn.db.enrollments.aggregate([
            {'$match': {'user': ObjectId(session["id"])}},
            {'$lookup': {
                'from': 'classes', 'localField': 'class',
                'foreignField': '_id', 'as': 'class'}},
            {'$unwind': {'path': '$class'}},
            {'$replaceRoot': {'newRoot': '$class'}}
        ])

        return render_template("home.html", session=session, courses=courses)


@frontend.route("/c/<code>")
def course_page(code):
    """Renders the appropriate course page for a user.

    TODO: Add a way to determine if user is enrolled in the course
            specified by the code in the URL
    """

    # look up data from db
    course = db_conn.db.classes.aggregate([
        {'$match': {'_id': ObjectId(code)}},
        {'$lookup': {
            'from': 'enrollments', 'localField': '_id',
            'foreignField': 'class', 'as': 'enrolled'}},
        {'$lookup': {
            'from': 'users', 'localField': 'enrolled.user',
            'foreignField': '_id', 'as': 'enrolled'}},
        {'$lookup': {
            'from': 'assignments', 'localField': '_id',
            'foreignField': 'class', 'as': 'assignments'}},
        {'$project': {'enrolled.password': 0}},
        {'$limit': 1}
    ])

    # try and get result, otherwise 404
    try:
        course = course.next()
    except StopIteration:
        abort(404)

    print(session)
    return render_template("course.html", session=session, course=course)


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
