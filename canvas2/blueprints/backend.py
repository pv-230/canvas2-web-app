from bson import ObjectId
from datetime import datetime
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
    """Submits an assignment to the database."""

    # get data from form
    print(request.form)
    assgid = request.form["assg-id"]
    contents = request.form["assg-entry"]
    course = request.form["assg-course"]
    userid = request.form["assg-user-id"]

    # ensure user is submitting own document
    if not userid == session["id"]:
        abort(403)

    # make sure user is enrolled in course
    temp = db_conn.db.enrollments.find_one({
        "user": ObjectId(userid), "class": ObjectId(course)
    })
    if not temp:
        abort(403)

    # make sure desired assignment even exists
    temp = db_conn.db.assignments.find_one({
        "_id": ObjectId(assgid), "class": ObjectId(course)
    })
    if not temp:
        abort(400)

    # save submission to db
    db_conn.db.submissions.insert_one({
        "assignment": ObjectId(assgid),
        "class": ObjectId(course),
        "user": ObjectId(userid),
        "contents": contents,
        "timestamp": datetime.now(),
        "comments": []
    })

    # return success message
    return redirect(url_for("frontend.course_page", code=course))


@backend.route("/add-assignment", methods=["POST"])
def add_assignment():
    """Adds an assignment to the database."""

    # get data from form
    title = request.form["assg-name"]
    desc = request.form["assg-desc"]
    duedate = request.form["due-date"]
    classid = request.form["course-code"]

    # ensure user is a teacher in the course
    temp1 = db_conn.db.users.find_one({"_id": ObjectId(session["id"])})
    temp2 = db_conn.db.enrollments.find_one({
        "user": ObjectId(session["id"]), "class": ObjectId(classid)
    })
    if not temp1 or not temp2:
        abort(403)
    elif not temp1["role"] >= 3:
        abort(403)

    # make assignment in database
    db_conn.db.assignments.insert_one({
        "title": title,
        "description": desc,
        "deadline": datetime.strptime(duedate, "%Y-%m-%dT%H:%M"),
        "class": ObjectId(classid),
    })

    # redirect to course page
    return redirect(url_for("frontend.course_page", code=classid))
