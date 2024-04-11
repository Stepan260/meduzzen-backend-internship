from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.postgres import get_session
from app.db.redisdb import redis_connection

router = APIRouter()


@router.get("/")
def root_handler():
    return {
        "status_code": 200,
        "detail": "ok",
        "result": "working"
    }


@router.get('/test_db')
async def test_db(session: AsyncSession = Depends(get_session)):
    return {
        # if not session and not redis connection it means that there is not connection to dbs
        'status_code': 200 if session and redis_connection else 500
    }
