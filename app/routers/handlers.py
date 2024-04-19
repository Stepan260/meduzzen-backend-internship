from fastapi import status, Request
from fastapi.responses import JSONResponse

from app.service.сustom_exception import ObjectNotFound


def handle_object_not_found(_: Request, exc: ObjectNotFound) -> JSONResponse:
    return JSONResponse(
        content={"message": str(exc)},
        status_code=status.HTTP_404_NOT_FOUND
    )
