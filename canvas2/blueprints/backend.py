from bson import ObjectId
from flask import Blueprint, request, session, redirect, url_for, abort

from ..utils.db import db_conn

# create main backend blueprint
backend = Blueprint(
    'backend', __name__,
    url_prefix="/secretary",  # cute nickname for backend ops, can be changed
)


@backend.route("/add-course", methods=["POST"])
def add_course():
    """Adds a course to the database.

    TODO: Need to add functionality here to add a course into the database
    TODO: Add more form data as needed, going with bare minimum for now
    TODO: Sanitize form input
    """

    # make sure user is authorized
    if "id" not in session:
        abort(401)
    elif not session["role"] >= 3:
        abort(403)

    # get data from form
    title = request.form["course-name"]
    code = request.form["course-code"]
    desc = request.form["course-desc"]

    # make class in database
    class_id = db_conn.db.classes.insert_one({
        "title": title,
        "code": code,
        "desc": desc,
    })

    # go ahead and enroll this teacher in the course
    db_conn.db.enrollments.insert_one({
        "user": ObjectId(session["id"]),
        "class": ObjectId(class_id.inserted_id),
    })

    # return success message
    return redirect(url_for("frontend.index"))


@backend.route("/submit-assignment", methods=["POST"])
def submit_assignment():
    """Submits an assignment to the database.

    TODO: Need to add a function here to save a student's submission to db
    """

    courseCode = request.form["course-code"]
    return redirect(courseCode)


@backend.route("/add-assignment", methods=["POST"])
def add_assignment():
    """Adds an assignment to the database.

    TODO: Need to add functionality here to add an assignment into the db
    """

    courseCode = request.form["course-code"]
    return redirect(courseCode)