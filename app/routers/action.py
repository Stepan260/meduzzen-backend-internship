from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from app.repository.action_repository import ActionRepository
from app.repository.company_repository import CompanyRepository
from app.repository.users_repository import UserRepository

from app.schemas.action import ActionSchema, BaseInviteSchema, ActionRequestSchema, BaseRequestSchema, \
    UserRequestsResponse, UserInvitesResponse, CompanyUsersResponse
from app.schemas.user import UserDetail
from app.service.action_service import ActionsService
from app.db.postgres import get_session
from app.service.auth_service import AuthService
from app.utils.enum import ActionType

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


# --------------------------------------Invites--------------------------------------
@router.post("/invite/create/", response_model=ActionSchema, status_code=status.HTTP_201_CREATED)
async def create_invite(
        invite_create: BaseInviteSchema,
        actions_service: ActionsService = Depends(get_actions_service),
        current_user: UserDetail = Depends(AuthService.get_current_user)
):
    current_user_uuid = current_user.uuid
    return await actions_service.create_invite(invite_create=invite_create, current_user_uuid=current_user_uuid)


@router.post("/invite/cancel/", status_code=status.HTTP_204_NO_CONTENT)
async def cancel_invite(
        action_uuid: UUID,
        actions_service: ActionsService = Depends(get_actions_service),
        current_user: UserDetail = Depends(AuthService.get_current_user)
):
    current_user_uuid = current_user.uuid
    return await actions_service.cancel_invite(action_uuid=action_uuid, current_user_uuid=current_user_uuid)


@router.post("/invite/accept/", status_code=status.HTTP_200_OK)
async def accept_invite(
        action_uuid: UUID,
        actions_service: ActionsService = Depends(get_actions_service),
        current_user: UserDetail = Depends(AuthService.get_current_user)
):
    return await actions_service.accept_or_decline_invite(
        action_type=ActionType.ACCEPT,
        action_uuid=action_uuid,
        current_user_uuid=current_user.uuid
    )


@router.post("/invite/decline/", status_code=status.HTTP_200_OK)
async def decline_invite(
        action_uuid: UUID,
        actions_service: ActionsService = Depends(get_actions_service),
        current_user: UserDetail = Depends(AuthService.get_current_user)
):
    return await actions_service.accept_or_decline_invite(
        action_type=ActionType.DECLINE,
        action_uuid=action_uuid,
        current_user_uuid=current_user.uuid
    )


# --------------------------------------Requests--------------------------------------
@router.post("/request/create/", status_code=status.HTTP_201_CREATED)
async def create_request(
        request_create: BaseRequestSchema,
        actions_service: ActionsService = Depends(get_actions_service),
        current_user: UserDetail = Depends(AuthService.get_current_user)
):
    return await actions_service.create_request(request_create=request_create, current_user_uuid=current_user.uuid)


@router.post("/request/cancel/", status_code=status.HTTP_204_NO_CONTENT)
async def cancel_request(
        request_cancel: BaseRequestSchema,
        actions_service: ActionsService = Depends(get_actions_service),
        current_user: UserDetail = Depends(AuthService.get_current_user)
):
    return await actions_service.cancel_request(request_cancel=request_cancel, current_user_uuid=current_user.uuid)


@router.post("/request/accept/", status_code=status.HTTP_200_OK)
async def accept_request(
        request_accept: ActionRequestSchema,
        actions_service: ActionsService = Depends(get_actions_service),
        current_user: UserDetail = Depends(AuthService.get_current_user)
):
    return await actions_service.accept_or_decline_request(
        action_type=ActionType.ACCEPT,
        request_accept=request_accept,
        current_user_uuid=current_user.uuid
    )


@router.post("/request/decline/", status_code=status.HTTP_200_OK)
async def decline_request(
        request_accept: ActionRequestSchema,
        actions_service: ActionsService = Depends(get_actions_service),
        current_user: UserDetail = Depends(AuthService.get_current_user)
):
    return await actions_service.accept_or_decline_request(
        action_type=ActionType.DECLINE,
        request_accept=request_accept,
        current_user_uuid=current_user.uuid
    )


@router.delete("/remove/{company_uuid}/{user_uuid}", status_code=status.HTTP_200_OK)
async def remove_user_from_company(company_uuid: UUID,
                                   user_uuid: UUID,
                                   actions_service: ActionsService = Depends(get_actions_service),
                                   current_user: UserDetail = Depends(AuthService.get_current_user)):
    owner_uuid = current_user.uuid
    return await actions_service.remove_user(company_uuid=company_uuid, user_uuid=user_uuid, owner_uuid=owner_uuid)


@router.get("/user/requests", response_model=UserRequestsResponse)
async def get_user_requests(
        current_user: UserDetail = Depends(AuthService.get_current_user),
        actions_service: ActionsService = Depends(get_actions_service),
        skip: int = 1,
        limit: int = 10
):
    return await actions_service.get_user_requests(
        user_uuid=current_user.uuid,
        skip=skip,
        limit=limit
    )


@router.get("/user/invite", response_model=UserInvitesResponse)
async def get_user_invite(
        current_user: UserDetail = Depends(AuthService.get_current_user),
        actions_service: ActionsService = Depends(get_actions_service),
        skip: int = 1,
        limit: int = 10
):
    return await actions_service.get_user_invites(
        user_uuid=current_user.uuid,
        skip=skip,
        limit=limit
    )


@router.get("/company/{company_uuid}/join_requests", response_model=UserRequestsResponse)
async def get_company_requests(
        company_uuid: UUID,
        actions_service: ActionsService = Depends(get_actions_service),
        current_user: UserDetail = Depends(AuthService.get_current_user),
        skip: int = 1,
        limit: int = 10
):
    return await actions_service.get_join_requests(company_uuid=company_uuid, skip=skip, limit=limit)


@router.get("/company/{company_uuid}/invited_users", response_model=UserInvitesResponse)
async def get_invited_users(
        company_uuid: UUID,
        actions_service: ActionsService = Depends(get_actions_service),
        current_user: UserDetail = Depends(AuthService.get_current_user),
        skip: int = 1,
        limit: int = 10
):
    return await actions_service.get_invited_users(company_uuid=company_uuid, skip=skip, limit=limit,
                                                   user_uuid=current_user.uuid)


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
