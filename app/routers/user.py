from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.schemas.user import SignUpRequest, UserBase
from app.service.users_service import UserService
from app.db.postgres import get_session
from app.repository.users_repository import UserRepository

router = APIRouter(tags=["Users"], prefix='/users')


@router.post('/', response_model=UserBase)
async def create_user(user_create: SignUpRequest,
                      session: AsyncSession = Depends(get_session),
                      ):
    user_repository = UserRepository(session)
    user_service = UserService(session=session, repository=user_repository)
    return await user_service.create_user(user_create.model_dump())
