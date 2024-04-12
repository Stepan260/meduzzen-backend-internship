from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from loguru import logger

from app.сore.config import settings
from app.routers.routers import router


app = FastAPI()
app.include_router(router)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

logger.add("app.log", rotation="250 MB", compression="gzip", level="INFO")

if __name__ == "__main__":
    from uvicorn import run as uvicorn_run

    uvicorn_run(
        "app.main:app", host=settings.HOST, port=settings.PORT, reload=settings.PORT
    )
