from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from loguru import logger
from starlette import status

from app.сore.config import settings
from app.routers.routers import router
from app.routers import user, auth
from app.service.сustom_exception import ObjectNotFound, UserAlreadyExist, UserPermissionDenied

app = FastAPI()

app.include_router(router)
app.include_router(user.router)
app.include_router(auth.router)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(ObjectNotFound)
async def handle_object_not_found(_: Request, exc: ObjectNotFound) -> JSONResponse:
    return JSONResponse(
        content={"message": str(exc)},
        status_code=status.HTTP_404_NOT_FOUND
    )


@app.exception_handler(UserAlreadyExist)
async def handle_user_already_exist(_: Request, exc: UserAlreadyExist) -> JSONResponse:
    return JSONResponse(
        content={"message": str(exc)},
        status_code=status.HTTP_409_CONFLICT
    )


@app.exception_handler(UserPermissionDenied)
async def handler_user_permission_denied(_: Request, exc: UserPermissionDenied) -> JSONResponse:
    return JSONResponse(
        content={"message": str(exc)},
        status_code=status.HTTP_403_FORBIDDEN
    )


logger.add("app.log", rotation="250 MB", compression="zip", level="INFO")

if __name__ == "__main__":
    from uvicorn import run as uvicorn_run

    uvicorn_run(
        "app.main:app", host=settings.HOST, port=settings.PORT, reload=settings.PORT
    )
