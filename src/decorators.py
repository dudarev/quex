"""
decorators.py
Decorators for URL handlers
https://github.com/kamalgill/flask-appengine-template
"""

from functools import wraps
from google.appengine.api import users
from flask import redirect, request, abort


def admin_required(func):
    """Requires App Engine admin credentials"""
    @wraps(func)
    def decorated_view(*args, **kwargs):
        if users.get_current_user():
            if not users.is_current_user_admin():
                abort(401)  # Unauthorized
            return func(*args, **kwargs)
        return redirect(users.create_login_url(request.url))
    return decorated_view
