from bson import ObjectId
from flask import Blueprint, session, render_template, redirect, url_for, abort

from ..utils.db import db_conn


# create main frontend blueprint
frontend = Blueprint(
    "frontend",
    __name__,
    template_folder="templates",
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
        courses = db_conn.db.enrollments.aggregate(
            [
                {"$match": {"user": ObjectId(session["id"])}},
                {
                    "$lookup": {
                        "from": "classes",
                        "localField": "class",
                        "foreignField": "_id",
                        "as": "class",
                    }
                },
                {"$unwind": {"path": "$class"}},
                {"$replaceRoot": {"newRoot": "$class"}},
            ]
        )

        return render_template("home.html", session=session, courses=courses)


@frontend.route("/c/<code>")
def course_page(code):
    """Renders the appropriate course page for a user.

    TODO: Add a way to determine if user is enrolled in the course
            specified by the code in the URL
    """

    # look up data from db
    course = db_conn.db.classes.aggregate(
        [
            {"$match": {"_id": ObjectId(code)}},
            {
                "$lookup": {
                    "from": "enrollments",
                    "localField": "_id",
                    "foreignField": "class",
                    "as": "enrolled",
                }
            },
            {
                "$lookup": {
                    "from": "users",
                    "localField": "enrolled.user",
                    "foreignField": "_id",
                    "as": "enrolled",
                }
            },
            {
                "$lookup": {
                    "from": "assignments",
                    "localField": "_id",
                    "foreignField": "class",
                    "as": "assignments",
                }
            },
            {"$project": {"enrolled.password": 0}},
            {"$limit": 1},
        ]
    )

    # try and get result, otherwise 404
    try:
        course = course.next()
    except StopIteration:
        abort(404)

    # if student, get submissions and attach to course object
    if session["role"] == 1:

        # lookup against database
        submissions = db_conn.db.submissions.find(
            {
                "user": ObjectId(session["id"]),
                "assignment": {
                    "$in": [ObjectId(a["_id"]) for a in course["assignments"]]
                },
            }
        )
        course["submissions"] = {s["assignment"]: s for s in submissions}

    # return course page
    return render_template("course.html", session=session, course=course)


@frontend.route("/c/<cid>/a/<aid>")
def manage_assignment(aid, cid):
    """Renders the page where teachers can manage assignments."""

    # if not logged in, send to login
    if "id" not in session:
        return redirect(url_for("auth.login"))

    # Prevents page access by students
    if session["role"] < 2:
        abort(401)

    # Gets assignment information
    assg_info = db_conn.db.assignments.find_one({"_id": ObjectId(aid)})

    # Gets course information
    crs_info = db_conn.db.classes.find_one({"_id": ObjectId(cid)})

    # Builds an object containing all students and their submissions
    student_subs = db_conn.db.enrollments.aggregate(
        [
            {"$match": {"class": ObjectId(cid)}},
            {
                "$lookup": {
                    "from": "users",
                    "localField": "user",
                    "foreignField": "_id",
                    "as": "user",
                }
            },
            {"$unwind": {"path": "$user"}},
            {
                "$redact": {
                    "$cond": {
                        "if": {"$lt": ["$user.role", 2]},
                        "then": "$$KEEP",
                        "else": "$$PRUNE",
                    }
                }
            },
            {
                "$lookup": {
                    "from": "submissions",
                    "let": {"e_assg": ObjectId(aid), "e_user": "$user._id"},
                    "pipeline": [
                        {
                            "$match": {
                                "$expr": {
                                    "$and": [
                                        {"$eq": ["$$e_user", "$user"]},
                                        {"$eq": ["$$e_assg", "$assignment"]},
                                    ]
                                }
                            }
                        }
                    ],
                    "as": "assignment",
                }
            },
            {
                "$project": {
                    "user.password": 0,
                    "assignment.assignment": 0,
                    "assignment.class": 0,
                    "assignment.user": 0,
                    "assignment.contents": 0,
                    "assignment.parsedContents": 0
                }
            },
        ]
    )

    return render_template(
        "assignment.html",
        student_subs=student_subs,
        assg_info=assg_info,
        crs_info=crs_info
    )
