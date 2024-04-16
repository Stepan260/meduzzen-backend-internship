from uuid import UUID
from typing import List

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.schemas.user import SignUpRequest, UserBase, UserUpdate, UserDetail
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


@router.get('/{user_id}', response_model=UserBase)
async def get_user_by_id(user_id: UUID,
                         session: AsyncSession = Depends(get_session),
                         ):
    user_repository = UserRepository(session)
    user_service = UserService(session=session, repository=user_repository)
    return await user_service.get_user_by_id(user_id)


@router.put('/{user_id}', response_model=UserBase)
async def update_user(user_id: UUID, user_update: UserUpdate,
                      session: AsyncSession = Depends(get_session)):
    user_repository = UserRepository(session)
    user_service = UserService(session=session, repository=user_repository)
    return await user_service.update_user(user_id, user_update)


@router.get("/users/", response_model=List[UserDetail])
async def get_all_users(skip: int = 1, limit: int = 10, session: AsyncSession = Depends(get_session)):
    user_repository = UserRepository(session)
    user_service = UserService(session=session, repository=user_repository)
    users = await user_service.get_all_users(skip=skip, limit=limit)
    return users


@router.delete('/{user_id}', response_model=None)
async def delete_user(user_id: UUID,
                      session: AsyncSession = Depends(get_session)):
    user_repository = UserRepository(session)
    user_service = UserService(session=session, repository=user_repository)
    await user_service.delete_user(user_id)
    return None
