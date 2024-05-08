from uuid import UUID
from typing import List

from fastapi import APIRouter, Depends, Response
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from app.schemas.user import SignUpRequest, UserBase, UserUpdate, UserDetail
from app.service.auth_service import AuthService
from app.service.users_service import UserService
from app.db.postgres import get_session
from app.repository.users_repository import UserRepository

router = APIRouter(tags=["Users"], prefix='/users')


async def get_user_service(session: AsyncSession = Depends(get_session)) -> UserService:
    user_repository = UserRepository(session)
    return UserService(session=session, repository=user_repository)


@router.post('/', response_model=UserBase)
async def create_user(user_create: SignUpRequest,
                      user_service: UserService = Depends(get_user_service)):
    return await user_service.create_user(user_create.dict())


@router.get('/{user_uuid}', response_model=UserBase)
async def get_user_by_id(user_uuid: UUID,
                         user_service: UserService = Depends(get_user_service)):
    return await user_service.get_user_by_id(user_uuid)


@router.put('/{user_uuid}', response_model=UserBase)
async def update_user(user_uuid: UUID, user_update: UserUpdate,
                      current_user: UserDetail = Depends(AuthService.get_current_user),
                      user_service: UserService = Depends(get_user_service)):
    return await user_service.update_user(user_uuid, user_update, current_user)


@router.get("/users/", response_model=List[UserDetail])
async def get_all_users(skip: int = 1, limit: int = 10,
                        user_service: UserService = Depends(get_user_service)):
    return await user_service.get_all_users(skip=skip, limit=limit)


@router.delete('/{user_uuid}', response_model=None, response_class=Response)
async def delete_user(user_uuid: UUID,
                      user_service: UserService = Depends(get_user_service),
                      current_user: UserDetail = Depends(AuthService.get_current_user)):
    await user_service.delete_user(user_uuid, current_user)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
