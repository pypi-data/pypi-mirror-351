# NotLetters API Client

Asynchronous Python SDK for working with the [`https://api.notletters.com/v1`](https://api.notletters.com/v1) service API. Based on [stollen](https://github.com/py-stollen/stollen).

## Installation

```bash
pip install notletters
```

# MRE

```python
from notletters import NotLetters, EmailType

async with NotLetters(api_token="your_api_token") as api:
    letters = await api.get_letters(
        email="user@example.com",
        password="secret",
        search="example",
        star=False,
    )
    for letter in letters:
        print(letter.subject, letter.date)

    purchase = await api.buy_emails(count=2, type_email=EmailType.UNLIMITED)
    for email in purchase:
        print(email.password)

    change_result = await api.change_password(
        email="user@example.com",
        old_password="old",
        new_password="new"
    )
    print(change_result)

    me = await api.get_me()
    print(me.username, me.balance)
```
