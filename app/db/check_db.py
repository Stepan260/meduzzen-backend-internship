import redis.asyncio as redis
from sqlalchemy import select

from app.db.postgres import async_session, engine
from app.models.model import Test
from app.сore.config import settings


async def check_postgres_connection():
    try:
        async with async_session() as session:
            async with engine.begin() as conn:
                await conn.run_sync(Test.metadata.create_all)

            new_session = Test(name="test_value")
            session.add(new_session)
            await session.commit()

            query = select(Test)
            result = await session.execute(query)
            data = result.scalars().all()

            await session.delete(new_session)
            await session.commit()

            if any(item.name == "test_value" for item in data):
                return True
            else:
                return False
    except:
        return False


async def check_redis_connection():
    try:
        connection = await redis.from_url(settings.REDIS_URL)
        await connection.set("test_key", "test_value")
        value = await connection.get("test_key")
        await connection.close()
        if value == b"test_value":
            return True
        else:
            return False
    except:
        return False
