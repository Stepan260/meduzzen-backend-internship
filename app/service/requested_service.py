from uuid import UUID, uuid4

from sqlalchemy.ext.asyncio import AsyncSession

from app.repository.action_repository import ActionRepository
from app.repository.company_repository import CompanyRepository
from app.repository.requested_repository import RequestedRepository
from app.repository.users_repository import UserRepository
from app.schemas.action import ActionRequestSchema, BaseRequestSchema
from app.service.сustom_exception import UserPermissionDenied, ActionError
from app.utils.enum import CompanyRole, ActionType


class RequestedService:
    def __init__(
            self,
            session: AsyncSession,
            requested_repository: RequestedRepository,
            company_repository: CompanyRepository,
            user_repository: UserRepository
    ):
        self.session = session
        self.requested_repository = requested_repository
        self.company_repository = company_repository
        self.user_repository = user_repository

    async def create_request(self, request_create: BaseRequestSchema, current_user_uuid: UUID):
        await self.company_repository.get_one_by_params_or_404(uuid=request_create.company_uuid)

        existing_action = await self.requested_repository.get_one(
            company_uuid=request_create.company_uuid,
            user_uuid=current_user_uuid
        )
        if existing_action:
            if existing_action.role == CompanyRole.REQUESTED:
                raise ActionError("You already sent request to this company")
            if existing_action.role in (CompanyRole.MEMBER, CompanyRole.ADMIN, CompanyRole.OWNER):
                raise ActionError("You are in this company")
            if existing_action.role == CompanyRole.BLOCKED:
                raise ActionError("You cannot send request to this company")
            if existing_action.role == CompanyRole.INVITED:
                return await self.requested_repository.update_one(existing_action.uuid, dict(role=CompanyRole.MEMBER))

        await self.requested_repository.create_one(dict(
            **request_create.model_dump(),
            user_uuid=current_user_uuid,
            role=CompanyRole.REQUESTED
        ))
        return {"message": "Request created successfully"}

    async def cancel_request(self, request_cancel: BaseRequestSchema, current_user_uuid: UUID):
        existing_action = await self.requested_repository.get_one_by_params_or_404(
            company_uuid=request_cancel.company_uuid,
            user_uuid=current_user_uuid
        )
        await self.requested_repository.delete_one(str(existing_action.uuid))
        return {"message": "Request canceled successfully"}

    async def accept_or_decline_request(
            self,
            action_type: ActionType,
            request_accept: ActionRequestSchema,
            current_user_uuid: UUID
    ):
        company = await self.company_repository.get_one_by_params_or_404(uuid=request_accept.company_uuid)
        if company.owner_uuid != current_user_uuid:
            raise UserPermissionDenied()

        existing_action = await self.requested_repository.get_one_by_params_or_404(
            company_uuid=request_accept.company_uuid,
            user_uuid=request_accept.user_uuid
        )

        if existing_action.role in (CompanyRole.MEMBER, CompanyRole.OWNER, CompanyRole.ADMIN):
            raise ActionError("User is already in company")
        if existing_action.role == CompanyRole.REQUESTED:
            await self.requested_repository.update_one(
                existing_action.uuid,
                dict(role=CompanyRole.MEMBER if action_type == ActionType.ACCEPT else CompanyRole.DECLINED)
            )

        return {"message": f"Request {'accepted' if action_type == ActionType.ACCEPT else 'declined'} successfully"}

    async def get_user_requests(self, user_uuid: UUID, skip: int = 1, limit: int = 10) -> dict:
        user_requests = await self.requested_repository.get_many(
            skip=skip,
            limit=limit,
            user_uuid=user_uuid,
            role=CompanyRole.REQUESTED
        )
        return {"requests": user_requests}

    async def get_join_requests(self, company_uuid: UUID, skip: int = 1, limit: int = 10) -> dict:
        join_requests = await self.requested_repository.get_many(
            company_uuid=company_uuid,
            role=CompanyRole.REQUESTED,
            skip=skip,
            limit=limit
        )
        return {"requests": join_requests}
