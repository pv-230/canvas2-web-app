from bson import ObjectId
from datetime import datetime
from flask import Blueprint, request, session, redirect, url_for, abort
import json
import re

from ..plagiarism.jaccard.jaccardsimilarity import shinglesString
from ..plagiarism.simhash.similarsubstrings import getCommonSubstrings,\
    parseText
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
    if session["role"] != 4 and not enrollment:
        abort(403)  # forbidden

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
    if session["role"] != 4 and not enrollment:
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
            "parsedContents": shinglesString(contents),
            "timestamp": datetime.now(),
            "comments": [],
            "grade": 0.0,
        }
    )

    # return redirect to same page, forcing a refresh
    return redirect(request.referrer)


@backend.route("/edit-assg", methods=["POST"])
def edit_assignment():
    """Updates the details for an assignment"""

    # get data from form
    title = request.form["assg-name"]
    desc = request.form["assg-desc"]
    duedate = request.form["due-date"]
    classid = request.form["course-id"]
    assgid = request.form["assg-id"]

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
    if session["role"] != 4 and not enrollment:
        abort(403)  # forbidden

    # Updates the assignment in the database
    db_conn.db.assignments.update_one(
        {"_id": ObjectId(assgid)},
        {
            "$set": {
                "title": title,
                "description": desc,
                "deadline": datetime.strptime(duedate, "%Y-%m-%dT%H:%M"),
            }
        }
    )

    # return redirect to same page, forcing a refresh
    return redirect(request.referrer)


@backend.route("/s/<sid>/submission-info", methods=["GET", "POST"])
def submission_info(sid):

    # if not logged in, send to login
    if "id" not in session:
        return redirect(url_for("auth.login"))

    # Prevents access by students
    if session["role"] < 2:
        abort(401)

    # ensure user exists and is ta role or greater
    user = db_conn.db.users.find_one({"_id": ObjectId(session["id"])})
    if not user or not user["role"] >= 2:
        abort(403)  # forbidden

    # ensure user is enrolled in course
    sub = db_conn.db.submissions.find_one(
            {"_id": ObjectId(sid)},
            {"class": 1}
        )
    enrollment = db_conn.db.enrollments.find_one(
        {"user": user["_id"], "class": sub["class"]}
    )
    if session["role"] != 4 and not enrollment:
        abort(403)  # forbidden

    # Gets a submission's contents and comments
    if request.method == "GET":
        sub_info = db_conn.db.submissions.find_one(
            {"_id": ObjectId(sid)},
            {
                "contents": 1,
                "comments": 1,
                "grade": 1,
                "simscore": 1,
            }
        )

        return json.dumps(sub_info, default=str)

    # Updates the submission grade and adds a new comment (if either exists)
    if request.method == "POST":
        comment = request.form["comment"]
        grade = request.form["grade"]

        if comment:
            commentInfo = {
                "userid": ObjectId(session["id"]),
                "username": db_conn.db.users.find_one(
                    {"_id": ObjectId(session["id"])}
                )["username"],
                "contents": comment,
                "timestamp": datetime.now()
            }

            db_conn.db.submissions.update_one(
                {"_id": ObjectId(sid)},
                {
                    "$push": {
                        "comments": commentInfo
                    }
                }
            )

        if grade:
            db_conn.db.submissions.update_one(
                {"_id": ObjectId(sid)},
                {
                    "$set": {
                        "grade": float(grade)
                    }
                }
            )

        return redirect(request.referrer)


@backend.route('/update-grades', methods=["POST"])
def update_grades():
    """Allows the updating of grades for multiple submissions"""

    # if not logged in, send to login
    if "id" not in session:
        return redirect(url_for("auth.login"))

    # Prevents access by students
    if session["role"] < 2:
        abort(401)

    # ensure user exists and is ta role or greater
    user = db_conn.db.users.find_one({"_id": ObjectId(session["id"])})
    if not user or not user["role"] >= 2:
        abort(403)  # forbidden

    for id in request.json:
        # ensure user is enrolled in course that has the submission
        sub = db_conn.db.submissions.find_one(
                {"_id": ObjectId(id)},
                {"class": 1}
            )
        enrollment = db_conn.db.enrollments.find_one(
            {"user": user["_id"], "class": sub["class"]}
        )
        if session["role"] != 4 and not enrollment:
            abort(403)  # forbidden

        # Perform the update for a submission
        db_conn.db.submissions.update_one(
            {"_id": ObjectId(id)},
            {
                "$set": {
                    "grade": float(request.json[id])
                }
            }
        )

    return redirect(request.referrer)


@backend.route('/delete_assg', methods=["POST"])
def delete_assignment():
    """Deletes an submission from the database"""

    # if not logged in, send to login
    if "id" not in session:
        return redirect(url_for("auth.login"))

    # Prevents access by students
    if session["role"] < 2:
        abort(401)

    # ensure user exists and is ta role or greater
    user = db_conn.db.users.find_one({
        "_id": ObjectId(session["id"])
    })
    if not user or not user["role"] >= 2:
        abort(403)  # forbidden

    # remove the assignment from the database
    db_conn.db.assignments.delete_one({
        "_id": ObjectId(request.form["assg-id"])
    })

    # return redirect to same page, forcing a refresh
    code = request.form['crs-code']
    return redirect(url_for("frontend.course_page", code=code))


@backend.route('/delete_sub', methods=["POST"])
def delete_submission():
    """Deletes an submission from the database"""

    # if not logged in, send to login
    if "id" not in session:
        return redirect(url_for("auth.login"))

    # Prevents access by students
    if session["role"] < 2:
        abort(401)

    # ensure user exists and is ta role or greater
    user = db_conn.db.users.find_one({
        "_id": ObjectId(session["id"])
    })
    if not user or not user["role"] >= 2:
        abort(403)  # forbidden

    # remove the assignment from the database
    db_conn.db.submissions.delete_one({
        "_id": ObjectId(request.form["sub-id"])
    })

    # return redirect to same page, forcing a refresh
    return redirect(request.referrer)


@backend.route("/s/<sid>/similarity-report", methods=["GET"])
def similarity_report(sid):

    # if not logged in, send to login
    if "id" not in session:
        return redirect(url_for("auth.login"))

    # Prevents access by students
    if session["role"] < 2:
        abort(401)

    # ensure user exists and is ta role or greater
    user = db_conn.db.users.find_one({"_id": ObjectId(session["id"])})
    if not user or not user["role"] >= 2:
        abort(403)

    # Gets a submission's contents and comments
    if request.method == "GET":
        sub_info = db_conn.db.submissions.find_one(
            {"_id": ObjectId(sid)},
            {
                "contents": 1,
                "comments": 1,
                "grade": 1,
                "simscore": 1,
                "simsub": 1,
            }
        )

    try:
        similar_sub_id = sub_info["simsub"]
    except Exception:
        return json.dumps({'error': 'No similar submissions'}, default=str)

    curr_contents = sub_info["contents"]

    # Get the contents of the similar submission
    similar_contents = db_conn.db.submissions.find_one(
        {"_id": ObjectId(similar_sub_id)},
        {
            "contents": 1,
        }
    )

    curr_contents_parsed = parseText(curr_contents)
    similar_contents_parsed = parseText(similar_contents["contents"])
    similar_sentences = getCommonSubstrings(
        curr_contents_parsed, similar_contents_parsed
    )

    sentences = []
    for i, j in similar_sentences:
        s1 = " ".join(curr_contents_parsed[i - 1])
        s2 = " ".join(similar_contents_parsed[j - 1])

        s1 = re.sub(r'\s+([^\s\w]|_)+', r'\1', s1)
        s2 = re.sub(r'\s+([^\s\w]|_)+', r'\1', s2)

        sentences.append((s1, s2))

    res = ""
    res += ("--------------- Similarity Report ---------------")
    res += ("\n")
    res += ("Similarity Score: " + str(sub_info["simscore"]))
    res += ("\n")
    res += ("# of Common Sentences: " + str(len(similar_sentences)))
    res += ("\n")
    res += ("\n")
    res += ("--------------- Similar Sentences ---------------")
    res += ("\n")
    for s1, s2 in sentences:
        res += ("Original: " + s1)
        res += ("\n")
        res += ("Similar: " + s2)
        res += ("\n")
        res += ("\n")

    return json.dumps(res, default=str)
