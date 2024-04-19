from typing import Any


class ObjectNotFound(Exception):
    def __init__(self, identifier: Any, model_name: str) -> None:
        super().__init__(f"{model_name} with the specified identifier - {identifier} not found")


class UserNotFound(ObjectNotFound):
    def __init__(self, identifier: Any, model_name: str = "user"):
        super().__init__(identifier, model_name)


class UserAlreadyExist(Exception):
    def __init__(self, identifier: str, model_name: str = "user"):
        super().__init__(f"{model_name} with the specified email {identifier} already exists.")
