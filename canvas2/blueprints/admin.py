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
    if session["role"] < 3:
        abort(401)

    return render_template("admin.html")
