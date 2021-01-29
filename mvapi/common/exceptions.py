class AppException(Exception):
    pass


class NotFoundError(AppException):
    pass


class AccessDeniedError(AppException):
    pass


class BadRequestError(AppException):
    pass


class UnauthorizedError(AppException):
    pass


class NotAllowedError(AppException):
    pass


class JWTError(AppException):
    pass


class AppValueError(AppException):
    pass


class UnexpectedArguments(AppException):
    pass


class ModelKeyError(AppException):
    pass
