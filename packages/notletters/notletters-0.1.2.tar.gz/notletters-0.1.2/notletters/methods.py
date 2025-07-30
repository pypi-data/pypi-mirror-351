from enum import Enum, unique
from typing import Optional

from pydantic import Field
from stollen import StollenMethod
from stollen.enums import HTTPMethod
from stollen.types import StollenT
from typing_extensions import NotRequired, TypedDict

from notletters.client import NotLetters
from notletters.responses import (
    BuyMailsResponse,
    ChangePasswordResponse,
    GetMeResponse,
    LettersResponse,
)


class NotLettersMethod(
    StollenMethod[StollenT, NotLetters],
    abstract=True,
):
    pass


class Filters(TypedDict, total=False):
    search: str
    star: NotRequired[bool]


class LettersMethod(
    NotLettersMethod[LettersResponse],
    http_method=HTTPMethod.POST,
    api_method="/letters",
    returning=LettersResponse,
    response_data_key=["letters"],
):
    email: str
    password: str = Field(repr=False)
    filters: Optional[Filters] = None


class ChangePasswordMethod(
    NotLettersMethod[ChangePasswordResponse],
    http_method=HTTPMethod.POST,
    api_method="/change-password",
    returning=ChangePasswordResponse,
):
    email: str
    new_password: str = Field(repr=False)
    old_password: str = Field(repr=False)


@unique
class EmailType(int, Enum):
    LIMIT = 0
    UNLIMITED = 1
    RU_ZONE = 2
    PERSONAL = 3


class BuyEmailsMethod(
    NotLettersMethod[BuyMailsResponse],
    http_method=HTTPMethod.POST,
    api_method="/buy-emails",
    returning=BuyMailsResponse,
):
    count: int = Field(ge=1)
    type_email: int


class GetMeMethod(
    NotLettersMethod[GetMeResponse],
    http_method=HTTPMethod.GET,
    api_method="/me",
    returning=GetMeResponse,
):
    pass
