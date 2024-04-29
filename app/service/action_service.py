from uuid import UUID, uuid4

from sqlalchemy.ext.asyncio import AsyncSession

from app.repository.action_repository import ActionRepository
from app.repository.company_repository import CompanyRepository
from app.repository.users_repository import UserRepository
from app.schemas.action import ActionRequestSchema, BaseRequestSchema, BaseInviteSchema
from app.service.сustom_exception import UserPermissionDenied, CompanyNotFound, UserNotFound, ActionError
from app.utils.enum import CompanyRole, ActionType


class ActionsService:
    def __init__(
            self,
            session: AsyncSession,
            action_repository: ActionRepository,
            company_repository: CompanyRepository,
            user_repository: UserRepository
    ):
        self.session = session
        self.action_repository = action_repository
        self.company_repository = company_repository
        self.user_repository = user_repository

    # --------------------------------------Invites--------------------------------------
    async def create_invite(self, invite_create: BaseInviteSchema, current_user_uuid: UUID):
        company = await self.company_repository.get_one_by_params_or_404(uuid=invite_create.company_uuid)

        if company.owner_uuid != current_user_uuid:
            raise UserPermissionDenied()

        await self.user_repository.get_one_by_params_or_404(uuid=invite_create.user_uuid)

        existing_action = await self.action_repository.get_one(
            company_uuid=invite_create.company_uuid,
            user_uuid=invite_create.user_uuid
        )
        if existing_action:
            if existing_action.role == CompanyRole.INVITED:
                raise ActionError("User is already invited to the company")
            elif existing_action.role == CompanyRole.MEMBER:
                raise ActionError("User is already a member of the company")
            elif existing_action.role == CompanyRole.BLOCKED:
                raise ActionError('User is blocked and cannot be invited')
            elif existing_action.role == CompanyRole.REQUESTED:
                return await self.action_repository.update_one(existing_action.uuid, dict(role=CompanyRole.MEMBER))

        return await self.action_repository.create_one(dict(
            **invite_create.model_dump(),
            role=CompanyRole.INVITED
        ))

    async def cancel_invite(self, action_uuid: UUID, current_user_uuid: UUID):
        invite = await self.action_repository.get_one_by_params_or_404(uuid=action_uuid)

        company = await self.company_repository.get_one_by_params_or_404(uuid=invite.company_uuid)

        if company.owner_uuid != current_user_uuid:
            raise UserPermissionDenied()

        return await self.action_repository.delete_one(str(action_uuid))

    async def accept_or_decline_invite(
            self,
            action_type: ActionType,
            action_uuid: UUID,
            current_user_uuid: UUID
    ):
        invite = await self.action_repository.get_one_by_params_or_404(uuid=action_uuid)

        if invite.user_uuid != current_user_uuid:
            raise UserPermissionDenied()

        if invite.role != CompanyRole.INVITED:
            raise ActionError("Invite is not in an acceptable state")

        if action_type == ActionType.ACCEPT:
            await self.action_repository.update_one(invite.uuid, {"role": CompanyRole.MEMBER})
            return {"message": "Invite accepted successfully, you are now a member of the company"}

        elif action_type == ActionType.DECLINE:
            await self.action_repository.update_one(invite.uuid, {"role": CompanyRole.DECLINED})
            return {"message": "Invite declined successfully"}

    # --------------------------------------Requests--------------------------------------
    async def create_request(self, request_create: BaseRequestSchema, current_user_uuid: UUID):
        await self.company_repository.get_one_by_params_or_404(uuid=request_create.company_uuid)

        existing_action = await self.action_repository.get_one(
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
                return await self.action_repository.update_one(existing_action.uuid, dict(role=CompanyRole.MEMBER))

        await self.action_repository.create_one(dict(
            **request_create.model_dump(),
            user_uuid=current_user_uuid,
            role=CompanyRole.REQUESTED
        ))
        return {"message": "Request created successfully"}

    async def cancel_request(self, request_cancel: BaseRequestSchema, current_user_uuid: UUID):
        existing_action = await self.action_repository.get_one_by_params_or_404(
            company_uuid=request_cancel.company_uuid,
            user_uuid=current_user_uuid
        )
        await self.action_repository.delete_one(str(existing_action.uuid))
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

        existing_action = await self.action_repository.get_one_by_params_or_404(
            company_uuid=request_accept.company_uuid,
            user_uuid=request_accept.user_uuid
        )

        if existing_action.role in (CompanyRole.MEMBER, CompanyRole.OWNER, CompanyRole.ADMIN):
            raise ActionError("User is already in company")
        if existing_action.role == CompanyRole.REQUESTED:
            await self.action_repository.update_one(
                existing_action.uuid,
                dict(role=CompanyRole.MEMBER if action_type == ActionType.ACCEPT else CompanyRole.DECLINED)
            )

        return {"message": f"Request {'accepted' if action_type == ActionType.ACCEPT else 'declined'} successfully"}

    async def remove_user(self, company_uuid: UUID, user_uuid: UUID, owner_uuid: UUID):
        company = await self.company_repository.get_one_by_params_or_404(uuid=company_uuid)
        if company.owner_uuid != owner_uuid:
            raise ActionError("You don't have permission to remove users from this company")

        user_role = await self.action_repository.get_one(company_uuid=company_uuid, user_uuid=user_uuid)
        if not user_role:
            raise UserNotFound(identifier=user_uuid)

        if user_role.role == CompanyRole.MEMBER:
            await self.action_repository.delete_one(user_role.uuid)
            return {"message": "User removed successfully from the company"}
        else:
            raise ActionError("User cannot be removed")

    async def get_user_requests(self, user_uuid: UUID, skip: int = 1, limit: int = 10) -> dict:
        user_requests = await self.action_repository.get_many(
            skip=skip,
            limit=limit,
            user_uuid=user_uuid,
            role=CompanyRole.REQUESTED
        )
        return {"requests": user_requests}

    async def get_user_invites(self, user_uuid: UUID, company_uuid: UUID, skip: int = 1, limit: int = 10) -> dict:
        company = await self.company_repository.get_one_by_params_or_404(uuid=company_uuid)

        if company.owner_uuid != user_uuid:
            raise UserPermissionDenied()

        user_invites = await self.action_repository.get_many(
            skip=skip,
            limit=limit,
            user_uuid=user_uuid,
            role=CompanyRole.INVITED
        )
        return {"invites": user_invites}

    async def get_join_requests(self, company_uuid: UUID, skip: int = 1, limit: int = 10) -> dict:
        join_requests = await self.action_repository.get_many(
            company_uuid=company_uuid,
            role=CompanyRole.REQUESTED,
            skip=skip,
            limit=limit
        )
        return {"requests": join_requests}

    async def get_invited_users(self, company_uuid: UUID, user_uuid: UUID, skip: int = 1, limit: int = 10) -> dict:
        company = await self.company_repository.get_one_by_params_or_404(uuid=company_uuid)

        if company.owner_uuid != user_uuid:
            raise UserPermissionDenied()

        invited_users = await self.action_repository.get_many(
            company_uuid=company_uuid,
            role=CompanyRole.INVITED,
            skip=skip,
            limit=limit
        )
        return {"invited_users": invited_users}

    async def get_company_users(self, company_uuid: UUID, user_uuid: UUID, skip: int = 1, limit: int = 10) -> dict:
        company = await self.company_repository.get_one_by_params_or_404(uuid=company_uuid)

        if company.owner_uuid != user_uuid:
            raise UserPermissionDenied()

        company_users = await self.action_repository.get_many(
            company_uuid=company_uuid,
            role=CompanyRole.MEMBER,
            skip=skip,
            limit=limit
        )

        if not company_users:
            raise CompanyNotFound(identifier='uuid')

        return {"users": company_users}
