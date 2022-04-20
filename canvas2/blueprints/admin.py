from bson import ObjectId
import json
from flask import Blueprint, request, session, render_template, redirect, \
    url_for, flash, abort

from ..utils.db import db_conn

# create main frontend blueprint
admin = Blueprint(
    "admin",
    __name__,
    url_prefix="/admin",
)


@admin.route("/panel", methods=["GET"])
def panel():
    """
    Renders the administrator's panel.
    """

    # if not logged in, send to login
    if "id" not in session:
        flash("You are not logged in!", "error")
        return redirect(url_for("auth.login"))

    # Prevents page access by non-admins
    if session["role"] < 4:
        abort(401)

    requests = db_conn.db.users.find(
        {"approved": False},
        {"password": 0}
    )

    # List casts help with template rendering
    req_list = list(requests)
    return render_template("admin.html", requests=req_list)


@admin.route("/action/<type>", methods=["POST"])
def action(type):
    """
    Performs an administrative action.
    """

    # if not logged in, send to login
    if "id" not in session:
        flash("You are not logged in!", "error")
        return redirect(url_for("auth.login"))

    # Prevents page access by non-admins
    if session["role"] < 4:
        abort(401)

    # Approves a teacher account
    if type == "approveRequest":
        db_conn.db.users.update_one(
            {"_id": ObjectId(request.form["approve-id"])},
            {
                "$set": {
                    "approved": True
                }
            }
        )

    # Denies a teacher account
    if type == "denyRequest":
        db_conn.db.users.delete_one(
            {"_id": ObjectId(request.form["deny-id"])}
        )

    # Updates a user's information
    if type == "updateUserInfo":
        userData = request.json
        db_conn.db.users.update_one(
            {"_id": ObjectId(userData[4])},
            {
                "$set": {
                    "lastname": userData[0],
                    "firstname": userData[1],
                    "username": userData[2],
                    "email": userData[3],
                }
            }
        )

    return redirect(url_for("admin.panel"))


@admin.route("/search-users", methods=["POST"])
def search_users():
    """
    Returns a JSON response containing matching users.
    """

    # if not logged in, send to login
    if "id" not in session:
        flash("You are not logged in!", "error")
        return redirect(url_for("auth.login"))

    # Prevents page access by non-admins
    if session["role"] < 4:
        abort(401)

    # Searches for users with fields that match the search string
    users = db_conn.db.users.find(
        {
            "$or": [
                {"firstname": {"$regex": f"^{request.json}", "$options": "i"}},
                {"lastname": {"$regex": f"^{request.json}", "$options": "i"}},
                {"username": {"$regex": f"^{request.json}", "$options": "i"}},
                {"email": {"$regex": f"^{request.json}", "$options": "i"}}
            ]
        }
    )

    # Convert to dict
    usersList = list(users)
    usersDict = dict()
    for user in usersList:
        user['_id'] = str(user["_id"])
        usersDict[user['_id']] = user

    return json.dumps(usersDict, default=str)
