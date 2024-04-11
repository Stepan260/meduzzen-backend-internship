from fastapi import APIRouter, Depends

from app.db.check_db import check_postgres_connection, check_redis_connection

router = APIRouter()

@router.get("/")
def root_handler():
    return {
        "status_code": 200,
        "detail": "ok",
        "result": "working"
    }


@router.get('/test_db')
async def db_test():
    postgres_conn = await check_postgres_connection()
    redis_conn = await check_redis_connection()
    if postgres_conn and redis_conn:
        return {
            "status_code": 200,
            "detail": "Databases are connected and working.",
            "result": {
                "redis": "connected",
                "postgres": "connected"
            }
        }
    else:
        return {
            "status_code": 200,
            "detail": "Databases are not connected"
        }
