# ruff: noqa: PLC0415
# lazy import to avoid circular dependencies
# and preserve backward compatibility
# if methods are removed or changed

from http import HTTPStatus
from typing import TYPE_CHECKING, Any

from stollen import Stollen
from stollen.requests import Header
from typing_extensions import Unpack

from notletters.exceptions import (
    NotLettersAPIError,
    NotLettersBadRequestError,
    NotLettersForbiddenError,
    NotLettersInternalServerError,
    NotLettersNotFoundError,
    NotLettersPaymentRequiredError,
    NotLettersUnauthorizedError,
)


if TYPE_CHECKING:
    from notletters.methods import (
        BuyEmailsMethod,
        ChangePasswordMethod,
        Filters,
        GetMeMethod,
        LettersMethod,
    )


class NotLetters(Stollen):
    def __init__(self, api_token: str, **stollen_kwargs: Any) -> None:
        super().__init__(
            base_url="https://api.notletters.com/v1",
            global_request_fields=[Header(name="Authorization", value=f"Bearer {api_token}")],
            response_data_key=["data"],
            error_message_key=["error"],
            general_error_class=NotLettersAPIError,
            error_codes={
                HTTPStatus.BAD_REQUEST: NotLettersBadRequestError,  # 400
                HTTPStatus.UNAUTHORIZED: NotLettersUnauthorizedError,  # 401
                HTTPStatus.PAYMENT_REQUIRED: NotLettersPaymentRequiredError,  # 402
                HTTPStatus.FORBIDDEN: NotLettersForbiddenError,  # 403
                HTTPStatus.NOT_FOUND: NotLettersNotFoundError,  # 404
                HTTPStatus.INTERNAL_SERVER_ERROR: NotLettersInternalServerError,  # 500
            },
            **stollen_kwargs,
        )

    def get_letters(
        self,
        email: str,
        password: str,
        **filters: Unpack["Filters"],
    ) -> "LettersMethod":
        from notletters.methods import LettersMethod

        return LettersMethod(
            email=email,
            password=password,
            filters=filters,
        ).as_(client=self)

    def change_password(
        self,
        email: str,
        new_password: str,
        old_password: str,
    ) -> "ChangePasswordMethod":
        from notletters.methods import ChangePasswordMethod

        return ChangePasswordMethod(
            email=email,
            new_password=new_password,
            old_password=old_password,
        ).as_(client=self)

    def buy_emails(
        self,
        count: int,
        type_email: int,
    ) -> "BuyEmailsMethod":
        from notletters.methods import BuyEmailsMethod

        return BuyEmailsMethod(
            count=count,
            type_email=type_email,
        ).as_(client=self)

    def get_me(self) -> "GetMeMethod":
        from notletters.methods import GetMeMethod

        return GetMeMethod().as_(client=self)
