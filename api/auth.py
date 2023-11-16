import os
import functools
from flask import Blueprint, g, redirect, render_template, request, session, url_for

bp = Blueprint('auth', __name__, url_prefix='/auth')


def auth_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if not g.authenticated:
            return redirect(url_for("auth.authenticate"))

        return view(**kwargs)

    return wrapped_view


@bp.route("/authenticate", methods=("GET", "POST"))
def authenticate():
    session.clear()
    if request.method == "POST":
        correct_password = os.environ.get("TP_RANDOM_AUTH")
        submitted_password = request.form["password"]
        if submitted_password == correct_password:
            session["authenticated"] = True
            return redirect(url_for("home"))

    return render_template("authenticate.html")


@bp.before_app_request
def load_authenticated_user():
    auth_status = session.get("authenticated")
    if not auth_status:
        g.authenticated = None
    else:
        g.authenticated = True
