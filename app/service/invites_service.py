from uuid import UUID, uuid4

from sqlalchemy.ext.asyncio import AsyncSession

from app.repository.company_repository import CompanyRepository
from app.repository.invites_repository import InvitesRepository
from app.repository.users_repository import UserRepository
from app.schemas.action import ActionRequestSchema, BaseRequestSchema, BaseInviteSchema
from app.service.сustom_exception import UserPermissionDenied, CompanyNotFound, UserNotFound, ActionError
from app.utils.enum import CompanyRole, ActionType


class InvitesService:
    def __init__(
            self,
            session: AsyncSession,
            invites_repository: InvitesRepository,
            company_repository: CompanyRepository,
            user_repository: UserRepository
    ):
        self.session = session
        self.invites_repository = invites_repository
        self.company_repository = company_repository
        self.user_repository = user_repository

    async def create_invite(self, invite_create: BaseInviteSchema, current_user_uuid: UUID):
        company = await self.company_repository.get_one_by_params_or_404(uuid=invite_create.company_uuid)

        if company.owner_uuid != current_user_uuid:
            raise UserPermissionDenied()

        await self.user_repository.get_one_by_params_or_404(uuid=invite_create.user_uuid)

        existing_action = await self.invites_repository.get_one(
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
                return await self.invites_repository.update_one(existing_action.uuid, dict(role=CompanyRole.MEMBER))

        return await self.invites_repository.create_one(dict(
            **invite_create.model_dump(),
            role=CompanyRole.INVITED
        ))

    async def cancel_invite(self, action_uuid: UUID, current_user_uuid: UUID):
        invite = await self.invites_repository.get_one_by_params_or_404(uuid=action_uuid)

        company = await self.company_repository.get_one_by_params_or_404(uuid=invite.company_uuid)

        if company.owner_uuid != current_user_uuid:
            raise UserPermissionDenied()

        return await self.invites_repository.delete_one(str(action_uuid))

    async def accept_or_decline_invite(
            self,
            action_type: ActionType,
            action_uuid: UUID,
            current_user_uuid: UUID
    ):
        invite = await self.invites_repository.get_one_by_params_or_404(uuid=action_uuid)

        if invite.user_uuid != current_user_uuid:
            raise UserPermissionDenied()

        if invite.role != CompanyRole.INVITED:
            raise ActionError("Invite is not in an acceptable state")

        if action_type == ActionType.ACCEPT:
            await self.invites_repository.update_one(invite.uuid, {"role": CompanyRole.MEMBER})
            return {"message": "Invite accepted successfully, you are now a member of the company"}

        elif action_type == ActionType.DECLINE:
            await self.invites_repository.update_one(invite.uuid, {"role": CompanyRole.DECLINED})
            return {"message": "Invite declined successfully"}

    async def get_user_invites(self, user_uuid: UUID, company_uuid: UUID, skip: int = 1, limit: int = 10) -> dict:
        company = await self.company_repository.get_one_by_params_or_404(uuid=company_uuid)

        if company.owner_uuid != user_uuid:
            raise UserPermissionDenied()

        user_invites = await self.invites_repository.get_many(
            skip=skip,
            limit=limit,
            user_uuid=user_uuid,
            role=CompanyRole.INVITED
        )
        return {"invites": user_invites}

    async def get_invited_users(self, company_uuid: UUID, user_uuid: UUID, skip: int = 1, limit: int = 10) -> dict:
        company = await self.company_repository.get_one_by_params_or_404(uuid=company_uuid)

        if company.owner_uuid != user_uuid:
            raise UserPermissionDenied()

        invited_users = await self.invites_repository.get_many(
            company_uuid=company_uuid,
            role=CompanyRole.INVITED,
            skip=skip,
            limit=limit
        )
        return {"invited_users": invited_users}
