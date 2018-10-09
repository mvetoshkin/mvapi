from functools import wraps

from flask import request
from werkzeug.exceptions import BadRequest

from .exceptions import AccessDeniedError, UnauthorizedError, BadRequestError


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


def owner_required(func):
    @wraps(func)
    def decorated_view(*args, **kwargs):
        self = args[0]

        user_id = kwargs.get('user_id')
        if not user_id:
            return func(*args, **kwargs)

        if not self.current_user:
            raise AccessDeniedError

        if not self.current_user.is_admin and self.current_user.id_ != user_id:
            raise AccessDeniedError

        return func(*args, **kwargs)

    return decorated_view


def json_payload_required(func):
    @wraps(func)
    def decorated_view(*args, **kwargs):
        try:
            # noinspection PyStatementEffect
            request.json
        except BadRequest:
            raise BadRequestError
        return func(*args, **kwargs)

    return decorated_view
