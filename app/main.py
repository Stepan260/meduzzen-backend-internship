from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers.routers import root_handler
from app.core.config import host, port, reload

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(root_handler)

if __name__ == "__main__":
    from uvicorn import run as uvicorn_run

    uvicorn_run("main:app", host=host, port=port, reload=reload)
