from mvapi.libs.exceptions import AppException


class NoBlueprintException(Exception):
    pass


class NoConverterException(Exception):
    pass


class NoExtensionException(Exception):
    pass


###

class AccessDeniedError(AppException):
    pass


class AppValueError(AppException):
    pass


class BadRequestError(AppException):
    pass


class JWTError(AppException):
    pass


class NotAllowedError(AppException):
    pass


class UnauthorizedError(AppException):
    pass


class UnexpectedArgumentsError(AppException):
    pass
