from typing import Any

"""Base handlers"""


class ObjectNotFound(Exception):
    def __init__(self, identifier: Any, model_name: str) -> None:
        super().__init__(f"{model_name} with the specified identifier - {identifier} not found")


class ObjectAlreadyExist(Exception):
    def __init__(self, identifier: Any, model_name: str) -> None:
        super().__init__(f"{model_name} with the specified identifier - {identifier} already exist")


"""User handlers"""


class UserPermissionDenied(Exception):
    def __init__(self) -> None:
        super().__init__("You do not have permission to update this")


class UserNotFound(ObjectNotFound):
    def __init__(self, identifier: Any, model_name: str = "user"):
        super().__init__(identifier, model_name)


class UserAlreadyExists(ObjectAlreadyExist):
    def __init__(self, identifier: Any, model_name: str = "user"):
        super().__init__(identifier, model_name)


"""Company handlers"""


class CompanyAlreadyExists(ObjectAlreadyExist):
    def __init__(self, identifier: Any, model_name: str = "company"):
        super().__init__(identifier, model_name)


class CompanyNotFound(ObjectNotFound):
    def __init__(self, identifier: Any, model_name: str = "company"):
        super().__init__(identifier, model_name)
