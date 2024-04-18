from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from loguru import logger
from starlette import status

from app.сore.config import settings
from app.routers.routers import router
from app.routers import user
from app.сore.сustom_exception import ObjectNotFound

app = FastAPI()

app.include_router(router)
app.include_router(user.router)

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


logger.add("app.log", rotation="250 MB", compression="zip", level="INFO")

if __name__ == "__main__":
    from uvicorn import run as uvicorn_run

    uvicorn_run(
        "app.main:app", host=settings.HOST, port=settings.PORT, reload=settings.PORT
    )
