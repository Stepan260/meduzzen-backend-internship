from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from app.repository.company_repository import CompanyRepository
from app.repository.requested_repository import RequestedRepository
from app.repository.users_repository import UserRepository

from app.schemas.action import ActionRequestSchema, BaseRequestSchema, UserRequestsResponse
from app.schemas.user import UserDetail
from app.db.postgres import get_session
from app.service.auth_service import AuthService
from app.service.requested_service import RequestedService
from app.utils.enum import ActionType

router = APIRouter(tags=["Request"])


async def get_request_service(session: AsyncSession = Depends(get_session)) -> RequestedService:
    requested_repository = RequestedRepository(session)
    company_repository = CompanyRepository(session)
    user_repository = UserRepository(session)

    return RequestedService(
        session=session,
        requested_repository=requested_repository,
        company_repository=company_repository,
        user_repository=user_repository
    )


@router.post("/request/create/", status_code=status.HTTP_201_CREATED)
async def create_request(
        request_create: BaseRequestSchema,
        requested_service: RequestedService = Depends(get_request_service),
        current_user: UserDetail = Depends(AuthService.get_current_user)
):
    return await requested_service.create_request(request_create=request_create, current_user_uuid=current_user.uuid)


@router.post("/request/cancel/", status_code=status.HTTP_204_NO_CONTENT)
async def cancel_request(
        request_cancel: BaseRequestSchema,
        requested_service: RequestedService = Depends(get_request_service),
        current_user: UserDetail = Depends(AuthService.get_current_user)
):
    return await requested_service.cancel_request(request_cancel=request_cancel, current_user_uuid=current_user.uuid)


@router.post("/request/accept/", status_code=status.HTTP_200_OK)
async def accept_request(
        request_accept: ActionRequestSchema,
        requested_service: RequestedService = Depends(get_request_service),
        current_user: UserDetail = Depends(AuthService.get_current_user)
):
    return await requested_service.accept_or_decline_request(
        action_type=ActionType.ACCEPT,
        request_accept=request_accept,
        current_user_uuid=current_user.uuid
    )


@router.post("/request/decline/", status_code=status.HTTP_200_OK)
async def decline_request(
        request_accept: ActionRequestSchema,
        requested_service: RequestedService = Depends(get_request_service),
        current_user: UserDetail = Depends(AuthService.get_current_user)
):
    return await requested_service.accept_or_decline_request(
        action_type=ActionType.DECLINE,
        request_accept=request_accept,
        current_user_uuid=current_user.uuid
    )


@router.get("/user/requests", response_model=UserRequestsResponse)
async def get_user_requests(
        current_user: UserDetail = Depends(AuthService.get_current_user),
        requested_service: RequestedService = Depends(get_request_service),
        skip: int = 1,
        limit: int = 10
):
    return await requested_service.get_user_requests(
        user_uuid=current_user.uuid,
        skip=skip,
        limit=limit
    )


@router.get("/company/{company_uuid}/join_requests", response_model=UserRequestsResponse)
async def get_company_requests(
        company_uuid: UUID,
        requested_service: RequestedService = Depends(get_request_service),
        current_user: UserDetail = Depends(AuthService.get_current_user),
        skip: int = 1,
        limit: int = 10
):
    return await requested_service.get_join_requests(company_uuid=company_uuid, skip=skip, limit=limit)
