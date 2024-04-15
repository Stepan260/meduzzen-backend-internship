from sqlalchemy.ext.asyncio import AsyncSession

from app.repository.users_repository import UserRepository
from app.schemas.user import UserDetail


class UserService:
    def __init__(self, session: AsyncSession, repository: UserRepository):
        self.repository = repository
        self.session = session

    async def create_user(self, user_create: dict) -> UserDetail:
        user_detail = await self.repository.create_one(user_create)
        return user_detail
