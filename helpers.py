from functools import wraps

from flask import redirect, render_template, request, session, url_for


def apology(top="", bottom=""):
    """Renders message as an apology to user."""
    return render_template("apology.html", top=top, bottom=bottom)


def login_required(f):
    """
    Decorate routes to require login.

    http://flask.pocoo.org/docs/0.11/patterns/viewdecorators/
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("admin_id") is None:
            return redirect(url_for("login"))
        return f(*args, **kwargs)
    return decorated_function


def root_login_required(f):
    """
    Decorates routes to require root login
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("admin_id") is not 1:
            return redirect(url_for("login"))
        return f(*args, **kwargs)
    return decorated_function
