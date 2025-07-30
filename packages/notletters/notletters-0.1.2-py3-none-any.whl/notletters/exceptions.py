from stollen.exceptions import StollenAPIError


class NotLettersError(Exception):
    pass


class NotLettersAPIError(StollenAPIError, NotLettersError):
    pass


class NotLettersBadRequestError(NotLettersAPIError):
    """400 Bad Request"""


class NotLettersUnauthorizedError(NotLettersAPIError):
    """401 Unauthorized"""


class NotLettersPaymentRequiredError(NotLettersAPIError):
    """402 Payment Required"""


class NotLettersForbiddenError(NotLettersAPIError):
    """403 Forbidden"""


class NotLettersNotFoundError(NotLettersAPIError):
    """404 Not Found"""


class NotLettersInternalServerError(NotLettersAPIError):
    """500 Internal Server Error"""
