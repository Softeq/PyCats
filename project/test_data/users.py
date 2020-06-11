from dataclasses import dataclass


@dataclass
class User:
    username: str
    password: str
    email: str


valid_user = User("cyrus8@ddividegs.com", "KturbqGfhjkm300", "cyrus8@ddividegs.com")
