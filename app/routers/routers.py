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

@router.get('/test_db/postgres')
async def db_postgres_test():
    postgres_conn = await check_postgres_connection()
    if postgres_conn:
        return {
            "status_code": 200,
            "detail": "PostgreSQL database is connected and working.",
            "result": {
                "postgres": "connected"
            }
        }
    else:
        return {
            "status_code": 200,
            "detail": "PostgreSQL database is not connected."
        }

@router.get('/test_db/redis')
async def db_redis_test():
    redis_conn = await check_redis_connection()
    if redis_conn:
        return {
            "status_code": 200,
            "detail": "Redis database is connected and working.",
            "result": {
                "redis": "connected"
            }
        }
    else:
        return {
            "status_code": 200,
            "detail": "Redis database is not connected."
        }