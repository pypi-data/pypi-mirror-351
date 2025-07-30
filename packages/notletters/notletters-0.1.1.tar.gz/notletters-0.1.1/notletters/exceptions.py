from stollen.exceptions import StollenAPIError


class NotLettersError(Exception):
    pass


class NotLettersAPIError(StollenAPIError, NotLettersError):
    pass


class NotLettersBadRequestError(NotLettersAPIError):
    """400 Bad Request"""

    message = "Bad request."


class NotLettersUnauthorizedError(NotLettersAPIError):
    """401 Unauthorized"""

    message = "Unauthorized."


class NotLettersPaymentRequiredError(NotLettersAPIError):
    """402 Payment Required"""

    message = "Payment required."


class NotLettersForbiddenError(NotLettersAPIError):
    """403 Forbidden"""

    message = "Forbidden."


class NotLettersNotFoundError(NotLettersAPIError):
    """404 Not Found"""

    message = "Resource not found."


class NotLettersInternalServerError(NotLettersAPIError):
    """500 Internal Server Error"""

    message = "Internal server error."
