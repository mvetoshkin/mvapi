from .exceptions import AccessDeniedError, UnauthorizedError


def auth_required(func):
    def decorated_view(*args, **kwargs):
        self = args[0]

        if not self.current_user:
            raise UnauthorizedError

        return func(*args, **kwargs)

    return decorated_view


def admin_required(func):
    @auth_required
    def decorated_view(*args, **kwargs):
        self = args[0]

        if not self.current_user.is_admin:
            raise AccessDeniedError

        return func(*args, **kwargs)

    return decorated_view


def owner_required(func):
    def decorated_view(*args, **kwargs):
        self = args[0]

        user_id = kwargs.get('user_id')
        if not user_id:
            return func(*args, **kwargs)

        if not self.current_user:
            raise AccessDeniedError

        if not self.current_user.is_admin and self.current_user.id != user_id:
            raise AccessDeniedError

        return func(*args, **kwargs)

    return decorated_view
