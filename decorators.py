from functools import wraps
from flask import abort
from flask_login import current_user


def role_required(*roles):
    """
    Usage:
        @role_required("admin")
        def dashboard(): ...

    Returns 403 Forbidden if the logged-in user's role isn't in `roles`.
    Always pair this with @login_required (placed above it) so
    current_user is guaranteed to exist first.
    """
    def decorator(f):
        @wraps(f)
        def wrapped(*args, **kwargs):
            if current_user.role not in roles:
                abort(403)
            return f(*args, **kwargs)
        return wrapped
    return decorator
