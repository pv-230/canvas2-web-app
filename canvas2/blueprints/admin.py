from bson import ObjectId
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

    # # find() always returns a cursor, even if no documents found
    # if (len(list(requests)) == 0):
    #     print("test")
    #     requests = None  # Helps with template rendering

    return render_template("admin.html", requests=requests)


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

    return redirect(url_for("admin.panel"))
