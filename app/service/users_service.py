from typing import List
from uuid import UUID

import bcrypt
from sqlalchemy.ext.asyncio import AsyncSession
from app.repository.users_repository import UserRepository
from app.schemas.user import UserDetail, UserUpdate, UserBase
from app.routers.сustom_exception import UserNotFound, UserAlreadyExist


class UserService:
    def __init__(self, session: AsyncSession, repository: UserRepository):
        self.repository = repository
        self.session = session

    async def create_user(self, user_create: dict) -> UserDetail:
        email = user_create.get('email')
        password = user_create.get('password')
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        db_user = await self.repository.get_one(email=email)
        if db_user:
            raise UserAlreadyExist(identifier=email)
        user_create['password'] = hashed_password
        user_detail = await self.repository.create_one(user_create)
        return user_detail

    async def get_user_by_id(self, user_uuid: UUID) -> UserBase:
        user = await self.repository.get_one(uuid=user_uuid)
        if not user:
            raise UserNotFound(identifier=user_uuid)
        return user

    async def update_user(self, user_uuid: UUID, user_update: UserUpdate) -> UserDetail:
        user_detail = await self.repository.get_one(uuid=str(user_uuid))
        if not user_detail:
            raise UserNotFound(identifier=user_uuid)

        updated_user = await self.repository.update_one(user_uuid, user_update.dict(exclude_unset=True))
        return updated_user

    async def get_all_users(self, skip: int = 1, limit: int = 10) -> List[UserDetail]:
        users = await self.repository.get_many(skip=skip, limit=limit)
        return users

    async def delete_user(self, user_uuid: UUID) -> None:
        user_detail = await self.repository.get_one(uuid=user_uuid)
        if not user_detail:
            raise UserNotFound(identifier=user_uuid)

        await self.repository.delete_one(str(user_uuid))
