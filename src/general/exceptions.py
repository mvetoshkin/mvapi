class AppException(Exception):
    def __init__(self, message=None):
        self.message = message


class NotFoundError(AppException):
    pass


class AccessDeniedError(AppException):
    pass


class BadRequestError(AppException):
    pass


class UnauthorizedError(AppException):
    pass


class JWTError(AppException):
    pass


class AppValueError(AppException):
    pass


class UnexpectedArguments(AppException):
    pass


class ModelKeyError(AppException):
    pass
