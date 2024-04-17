from uuid import UUID
from typing import List

from fastapi import APIRouter, Depends, Response,HTTPException
from sqlalchemy.ext.asyncio import AsyncSession, session
from starlette import status

from app.schemas.user import SignUpRequest, UserBase, UserUpdate, UserDetail
from app.service.users_service import UserService, UserAlreadyExistsException
from app.db.postgres import get_session
from app.repository.users_repository import UserRepository

router = APIRouter(tags=["Users"], prefix='/users')


async def get_user_service(session: AsyncSession = Depends(get_session)) -> UserService:
    user_repository = UserRepository(session)
    return UserService(session=session, repository=user_repository)


@router.post('/', response_model=UserBase)
async def create_user(user_create: SignUpRequest,
                      user_service: UserService = Depends(get_user_service)):
    try:
        return await user_service.create_user(user_create.model_dump())
    except UserAlreadyExistsException:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User already exists",
        )


@router.get('/{user_id}', response_model=UserBase)
async def get_user_by_id(user_id: UUID,
                         user_service: UserService = Depends(get_user_service)):
    return await user_service.get_user_by_id(user_id)


@router.put('/{user_id}', response_model=UserBase)
async def update_user(user_id: UUID, user_update: UserUpdate,
                      user_service: UserService = Depends(get_user_service)):
    return await user_service.update_user(user_id, user_update)


@router.get("/users/", response_model=List[UserDetail])
async def get_all_users(skip: int = 1, limit: int = 10,
                        user_service: UserService = Depends(get_user_service)):
    return await user_service.get_all_users(skip=skip, limit=limit)


@router.delete('/{user_id}', response_model=None, response_class=Response)
async def delete_user(user_id: UUID,
                      user_service: UserService = Depends(get_user_service)):
    await user_service.delete_user(user_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
