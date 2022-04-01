from bson import ObjectId
from datetime import datetime
from flask import Blueprint, request, session, redirect, url_for, abort

from ..utils.db import db_conn

# create main backend blueprint
backend = Blueprint(
    "backend",
    __name__,
    url_prefix="/secretary",  # cute nickname for backend ops, can be changed
)


@backend.route("/add-course", methods=["POST"])
def add_course():
    """Adds a course to the database."""

    # get data from form
    # TODO: Sanitize form input
    title = request.form["course-name"]
    code = request.form["course-code"]
    desc = request.form["course-desc"]

    # make sure at user is at least logged in
    if "id" not in session:
        abort(401)  # unauthorized

    # make sure user is permitted to do this operation
    # hard lookup, assuming session vars can be tampered with
    # NOTE: yes, this is kind of pointless because it uses the unsafe session
    #       'id' variable for the lookup. however at the bare minimum, 94-bit
    #       user IDs are harder to spoof than incrementing a single 'role'
    #       session integer, so i'm keeping it for now. -A
    userdata = db_conn.db.users.find_one({"_id": ObjectId(session["id"])})
    if not userdata["role"] >= 3:
        abort(403)  # forbidden

    # TODO: Add code to check if course already exists
    # NOTE: unsure if we'll want to implement this atm, because the same
    #       course can exist across multiple semesters. will still leave this
    #       reminder here for now tho. -A

    # make class in database
    new_class = db_conn.db.classes.insert_one(
        {
            "title": title,
            "code": code,
            "desc": desc,
        }
    )

    # go ahead and enroll this teacher in the course
    db_conn.db.enrollments.insert_one(
        {
            "user": ObjectId(session["id"]),
            "class": ObjectId(new_class.inserted_id),
        }
    )

    # return success message, redirect to new course page
    return redirect(
        url_for("frontend.course_page", code=new_class.inserted_id)
    )


@backend.route("/create-assg", methods=["POST"])
def add_assignment():
    """Adds an assignment to the database."""

    # get data from form
    title = request.form["assg-name"]
    desc = request.form["assg-desc"]
    duedate = request.form["due-date"]
    classid = request.form["course-code"]

    # make sure at user is at least logged in
    if "id" not in session:
        abort(401)  # unauthorized

    # ensure user exists and is a teacher
    teacher = db_conn.db.users.find_one({"_id": ObjectId(session["id"])})
    if not teacher or not teacher["role"] >= 3:
        abort(403)  # forbidden

    # ensure teacher is enrolled in course
    # NOTE: teacher['_id'] is already of form ObjectID, so no need to convert
    enrollment = db_conn.db.enrollments.find_one(
        {"user": teacher["_id"], "class": ObjectId(classid)}
    )
    if not enrollment:
        abort(403)  # forbidden

    # TODO: make sure assignment already submitted
    # NOTE: once again: it's possible we can have same title submissions,
    #       so this is not the best idea at the moment. -A

    # make assignment in database
    db_conn.db.assignments.insert_one(
        {
            "title": title,
            "description": desc,
            "deadline": datetime.strptime(duedate, "%Y-%m-%dT%H:%M"),
            "class": ObjectId(classid),
        }
    )

    # return redirect to same page, forcing a refresh
    return redirect(request.referrer)


@backend.route("/submit-assg", methods=["POST"])
def submit_assignment():
    """Submits an assignment to the database."""

    # get data from form
    # TODO: Sanitize form input
    assgid = request.form["assg-id"]
    contents = request.form["assg-entry"]
    userid = request.form["assg-user-id"]

    # make sure at user is at least logged in
    if "id" not in session:
        abort(401)  # unauthorized

    # make sure user exists and is a student
    user = db_conn.db.users.find_one({"_id": ObjectId(userid)})
    if not user:
        abort(400)  # bad request
    elif user["role"] != 1:
        abort(403)  # forbidden

    # ensure user is submitting own document
    if not userid == session["id"]:
        abort(403)  # forbidden

    # make sure desired assignment even exists
    assignment = db_conn.db.assignments.find_one({"_id": ObjectId(assgid)})
    if not assignment:
        abort(400)  # bad request

    # make sure user is enrolled in course
    # NOTE: assignment["class"] is already of form ObjectID, so no need to
    #       convert
    enrollment = db_conn.db.enrollments.find_one(
        {"user": ObjectId(userid), "class": assignment["class"]}
    )
    if not enrollment:
        abort(403)  # forbidden

    # make sure isnt already submitted
    # NOTE: this may change in the future; i.e. revisions, etc.
    temp = db_conn.db.submissions.find_one(
        {"user": ObjectId(userid), "assignment": ObjectId(assgid)}
    )
    if temp:
        abort(400)  # bad request

    # save submission to db
    db_conn.db.submissions.insert_one(
        {
            "assignment": ObjectId(assgid),
            "class": assignment["class"],
            "user": ObjectId(userid),
            "contents": contents,
            "timestamp": datetime.now(),
            "comments": [],
        }
    )

    # return redirect to same page, forcing a refresh
    return redirect(request.referrer)
