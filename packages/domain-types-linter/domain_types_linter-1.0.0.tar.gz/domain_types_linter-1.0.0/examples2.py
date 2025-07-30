from typing import NewType

UserId = NewType("UserId", int)

def get_user_id() -> "UserId":
    ...

def process_user(uid: "UserId"):
    ...

def user_handler():
    process_user(get_user_id())
