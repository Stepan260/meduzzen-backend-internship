from http.client import HTTPException
from typing import TypeVar, List
from datetime import datetime

from sqlalchemy import update, delete ,select
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from app.model.user import Base
from app.сore.сustom_exception import ObjectNotFound

ModelType = TypeVar("ModelType")


class BaseRepository:
    def __init__(self, session: AsyncSession, model: ModelType):
        self.session = session
        self.model = model

    async def create_one(self, data: dict) -> Base:
        row = self.model(**data)
        self.session.add(row)
        await self.session.commit()
        await self.session.refresh(row)
        return row

    async def create_many(self, data: List[dict]) -> List[Base]:
        rows = [self.model(**row) for row in data]
        self.session.bulk_save_objects(rows)
        await self.session.commit()
        return rows

    async def get_one(self, **params) -> Base:
        query = select(self.model).filter_by(**params)
        result = await self.session.execute(query)
        db_row = result.scalar_one_or_none()
        return db_row

    async def get_many(self, skip: int = 1, limit: int = 10, **params) -> List[Base]:
        offset = (skip - 1) * limit
        query = select(self.model).filter_by(**params).offset(offset).limit(limit)
        result = await self.session.execute(query)
        db_rows = result.scalars().all()
        return db_rows

    async def update_one(self, model_uuid: str, data: dict) -> Base:
        query = (
            update(self.model)
            .where(self.model.uuid == model_uuid)
            .values(**data)
            .returning(self.model)
        )
        res = await self.session.execute(query)
        res.updated_at = datetime.now()
        await self.session.commit()
        return res.scalar_one()

    async def delete_one(self, model_uuid: str) -> Base:
        query = (
            delete(self.model)
            .where(self.model.uuid == model_uuid)
            .returning(self.model)
        )
        res = await self.session.execute(query)
        await self.session.commit()
        return res.scalar_one()

    async def get_one_by_params_or_404(self, **params) -> Base:
        db_row = await self.get_one(**params)
        if not db_row:
            raise ObjectNotFound(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Object not found",
            )
        return db_row
