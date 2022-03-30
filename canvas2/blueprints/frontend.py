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
