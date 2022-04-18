import secrets
from bson import ObjectId
from datetime import datetime, timedelta
from flask import Blueprint, request, session, render_template, redirect,\
    url_for, abort, flash

from ..utils.db import db_conn

# NOTE: backend was getting cluttered so I moved over here. -A

# create main backend blueprint
invites = Blueprint(
    "invites",
    __name__,
    # url_prefix="/invite",
)


@invites.route("/c/<code>/invite", methods=["POST"])
def create_invite(code):
    """Makes an invite for a class."""

    # ensure user is logged in
    if "id" not in session:
        abort(401)

    # ensure user is permitted to do this operation
    if not session["role"] >= 3:
        abort(403)

    # ensure class even exists
    course = db_conn.db.classes.find_one(
        {
            "_id": ObjectId(code),
        }
    )
    if not course:
        abort(400)

    # ensure user is enrolled in the class
    enroll = db_conn.db.enrollments.find_one(
        {
            "user": ObjectId(session["id"]),
            "class": ObjectId(code)
        }
    )
    if not enroll:
        abort(401)

    # make invite code
    db_conn.db.invites.insert_one(
        {
            "class": ObjectId(code),
            "code": secrets.token_urlsafe(16),
            "expires": datetime.now() + timedelta(days=7),
        }
    )

    # return to referrer
    return redirect(request.referrer)


@invites.route("/j/<code>", methods=["GET", "POST"])
def join_invite(code):
    """
    GET: Renders the page where a user can join a class.
    POST: Joins a class using a given invite code.
    """

    # get invite data
    invite = db_conn.db.invites.find_one({"code": code})
    if not invite:
        abort(404)

    # get course data
    course = db_conn.db.classes.find_one({"_id": invite["class"]})
    if not course:
        abort(500)

    # if get, render page
    if request.method == "GET":

        # ensure user is logged in
        if "id" not in session:
            flash(
                "You must be logged in to perform this action! " +
                "Please log in or sign up first!", "error"
            )
            return redirect(url_for("auth.login"))

        # Redirects to course page if user already enrolled
        enrollment = db_conn.db.enrollments.find_one(
            {
                "user": ObjectId(session["id"]),
                "class": ObjectId(course["_id"]),
            }
        )
        if enrollment:
            return redirect(url_for("frontend.course_page", code=course["_id"]))  # noqa: E501

        return render_template("invitation.html", course=course, code=code)

    # if post, actually join the class
    elif request.method == "POST":

        # ensure logged in
        if "id" not in session:
            abort(401)  # unauthorized

        # enroll user in course
        db_conn.db.enrollments.insert_one(
            {
                "user": ObjectId(session["id"]),
                "class": ObjectId(course["_id"]),
            }
        )

        # redirect to course page
        return redirect(url_for("frontend.course_page", code=course["_id"]))
