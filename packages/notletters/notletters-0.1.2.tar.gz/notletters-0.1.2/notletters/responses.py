from datetime import datetime
from uuid import UUID

from pydantic import Field, model_serializer, model_validator
from stollen import StollenObject

from notletters.client import NotLetters


class NotLettersObject(StollenObject[NotLetters]):
    pass


class Mail(NotLettersObject):
    email: str
    password: str = Field(init=False)

    @model_validator(mode="before")
    @classmethod
    def _validate(cls, email_and_password: str) -> dict[str, str]:
        email, password = email_and_password.split(":")
        return {"email": email, "password": password}

    @model_serializer
    def _serialize(self) -> str:
        return f"{self.email}:{self.password}"


class LetterBody(NotLettersObject):
    html: str
    text: str


class Letter(NotLettersObject):
    id: UUID
    sender: str
    sender_name: str
    subject: str
    letter: LetterBody
    star: bool
    date: datetime


class GetMeResponse(NotLettersObject):
    id: UUID
    username: str
    balance: float
    rate_limit: int


BuyMailsResponse = list[Mail]
LettersResponse = list[Letter]
ChangePasswordResponse = str
