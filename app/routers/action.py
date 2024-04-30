from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from app.repository.action_repository import ActionRepository
from app.repository.company_repository import CompanyRepository
from app.repository.users_repository import UserRepository

from app.schemas.action import CompanyUsersResponse
from app.schemas.user import UserDetail
from app.service.action_service import ActionsService
from app.db.postgres import get_session
from app.service.auth_service import AuthService

router = APIRouter(tags=["Action"])


async def get_actions_service(session: AsyncSession = Depends(get_session)) -> ActionsService:
    action_repository = ActionRepository(session)
    company_repository = CompanyRepository(session)
    user_repository = UserRepository(session)

    return ActionsService(
        session=session,
        action_repository=action_repository,
        company_repository=company_repository,
        user_repository=user_repository
    )


@router.delete("/remove/{company_uuid}/{user_uuid}", status_code=status.HTTP_200_OK)
async def remove_user_from_company(company_uuid: UUID,
                                   user_uuid: UUID,
                                   actions_service: ActionsService = Depends(get_actions_service),
                                   current_user: UserDetail = Depends(AuthService.get_current_user)):
    owner_uuid = current_user.uuid
    return await actions_service.remove_user(company_uuid=company_uuid, user_uuid=user_uuid, owner_uuid=owner_uuid)


@router.get("/company/{company_uuid}/users", response_model=CompanyUsersResponse)
async def get_company_users(
        company_uuid: UUID,
        actions_service: ActionsService = Depends(get_actions_service),
        current_user: UserDetail = Depends(AuthService.get_current_user),
        skip: int = 1,
        limit: int = 10
):
    return await actions_service.get_company_users(company_uuid=company_uuid, skip=skip, limit=limit,
                                                   user_uuid=current_user.uuid)
