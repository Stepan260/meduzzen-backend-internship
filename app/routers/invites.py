from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from app.repository.company_repository import CompanyRepository
from app.repository.invites_repository import InvitesRepository
from app.repository.users_repository import UserRepository

from app.schemas.action import ActionSchema, BaseInviteSchema, UserInvitesResponse
from app.schemas.user import UserDetail

from app.db.postgres import get_session
from app.service.auth_service import AuthService
from app.service.invites_service import InvitesService
from app.utils.enum import ActionType

router = APIRouter(tags=["Invite"])


async def get_invites_service(session: AsyncSession = Depends(get_session)) -> InvitesService:
    invites_repository = InvitesRepository(session)
    company_repository = CompanyRepository(session)
    user_repository = UserRepository(session)

    return InvitesService(
        session=session,
        invites_repository=invites_repository,
        company_repository=company_repository,
        user_repository=user_repository
    )


@router.post("/invite/create/", response_model=ActionSchema, status_code=status.HTTP_201_CREATED)
async def create_invite(
        invite_create: BaseInviteSchema,
        invites_service: InvitesService = Depends(get_invites_service),
        current_user: UserDetail = Depends(AuthService.get_current_user)
):
    current_user_uuid = current_user.uuid
    return await invites_service.create_invite(invite_create=invite_create, current_user_uuid=current_user_uuid)


@router.post("/invite/cancel/", status_code=status.HTTP_204_NO_CONTENT)
async def cancel_invite(
        action_uuid: UUID,
        invites_service: InvitesService = Depends(get_invites_service),
        current_user: UserDetail = Depends(AuthService.get_current_user)
):
    current_user_uuid = current_user.uuid
    return await invites_service.cancel_invite(action_uuid=action_uuid, current_user_uuid=current_user_uuid)


@router.post("/invite/accept/", status_code=status.HTTP_200_OK)
async def accept_invite(
        action_uuid: UUID,
        invites_service: InvitesService = Depends(get_invites_service),
        current_user: UserDetail = Depends(AuthService.get_current_user)
):
    return await invites_service.accept_or_decline_invite(
        action_type=ActionType.ACCEPT,
        action_uuid=action_uuid,
        current_user_uuid=current_user.uuid
    )


@router.post("/invite/decline/", status_code=status.HTTP_200_OK)
async def decline_invite(
        action_uuid: UUID,
        invites_service: InvitesService = Depends(get_invites_service),
        current_user: UserDetail = Depends(AuthService.get_current_user)
):
    return await invites_service.accept_or_decline_invite(
        action_type=ActionType.DECLINE,
        action_uuid=action_uuid,
        current_user_uuid=current_user.uuid
    )


@router.get("/user/invite", response_model=UserInvitesResponse)
async def get_user_invite(
        current_user: UserDetail = Depends(AuthService.get_current_user),
        invites_service: InvitesService = Depends(get_invites_service),
        skip: int = 1,
        limit: int = 10
):
    return await invites_service.get_user_invites(
        user_uuid=current_user.uuid,
        skip=skip,
        limit=limit,
    )


@router.get("/company/{company_uuid}/invited_users", response_model=UserInvitesResponse)
async def get_invited_users(
        company_uuid: UUID,
        invites_service: InvitesService = Depends(get_invites_service),
        current_user: UserDetail = Depends(AuthService.get_current_user),
        skip: int = 1,
        limit: int = 10
):
    return await invites_service.get_invited_users(company_uuid=company_uuid, skip=skip, limit=limit,
                                                   user_uuid=current_user.uuid)
