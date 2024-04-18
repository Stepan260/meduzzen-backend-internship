from typing import Any
from fastapi import status, Request
from fastapi.responses import JSONResponse


class ObjectNotFound(Exception):
    def __init__(self, identifier: Any, model_name: str) -> None:
        super().__init__(f"{model_name} с указанным идентификатором - {identifier} не найден")


class UserNotFound(ObjectNotFound):
    def __init__(self, identifier: Any, model_name: str = "user"):
        super().__init__(identifier, model_name)


def handle_object_not_found(_: Request, exc: ObjectNotFound) -> JSONResponse:
    return JSONResponse(
        content={"message": str(exc)},
        status_code=status.HTTP_404_NOT_FOUND
    )
