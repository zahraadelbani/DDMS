"""Role based access control."""

from functools import wraps

from django.core.exceptions import PermissionDenied


def role_required(*allowed_roles):
    """Only lets the given roles open the page. Anyone else gets a 403."""

    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            if request.user.role not in allowed_roles:
                raise PermissionDenied
            return view_func(request, *args, **kwargs)

        return wrapper

    return decorator