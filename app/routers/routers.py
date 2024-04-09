from fastapi import APIRouter

router = APIRouter()

@router.get("/")
def root_handler():
    return {
        "status_code": 200,
        "detail": "ok",
        "result": "working"
    }