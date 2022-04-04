from functools import wraps

from mvapi.libs.exceptions import NotFoundError
from mvapi.settings import settings
from mvapi.web.libs.exceptions import AccessDeniedError, UnauthorizedError


def auth_required(func):
    @wraps(func)
    def decorated_view(*args, **kwargs):
        self = args[0]

        if not self.current_user:
            raise UnauthorizedError

        return func(*args, **kwargs)

    return decorated_view


def admin_required(func):
    @wraps(func)
    @auth_required
    def decorated_view(*args, **kwargs):
        self = args[0]

        if not self.current_user.is_admin:
            raise AccessDeniedError

        return func(*args, **kwargs)

    return decorated_view


def debug_only(func):
    @wraps(func)
    def decorated_view(*args, **kwargs):
        if not settings.DEBUG:
            raise NotFoundError

        return func(*args, **kwargs)

    return decorated_view
