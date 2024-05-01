from uuid import UUID, uuid4

from sqlalchemy.ext.asyncio import AsyncSession

from app.repository.action_repository import ActionRepository
from app.repository.company_repository import CompanyRepository
from app.repository.users_repository import UserRepository
from app.service.сustom_exception import UserPermissionDenied, CompanyNotFound, UserNotFound, ActionError
from app.utils.enum import CompanyRole


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

    async def remove_user(self, company_uuid: UUID, user_uuid: UUID, owner_uuid: UUID):
        company = await self.company_repository.get_one_by_params_or_404(uuid=company_uuid)
        if company.owner_uuid != owner_uuid:
            raise UserPermissionDenied()

        user_role = await self.action_repository.get_one(company_uuid=company_uuid, user_uuid=user_uuid)
        if not user_role:
            raise UserNotFound(identifier=user_uuid)

        if user_role.role == CompanyRole.MEMBER:
            await self.action_repository.delete_one(user_role.uuid)
            return {"message": "User removed successfully from the company"}
        else:
            raise ActionError("User cannot be removed")

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

    async def assign_admin(self, company_uuid: UUID, user_uuid: UUID, owner_uuid: UUID):
        company = await self.company_repository.get_one_by_params_or_404(uuid=company_uuid)

        if company.owner_uuid != owner_uuid:
            raise UserPermissionDenied()

        action = await self.action_repository.get_one_by_params_or_404(
            company_uuid=company_uuid,
            user_uuid=user_uuid
        )

        if action.role != CompanyRole.MEMBER:
            raise ActionError('User is not a member')

        await self.action_repository.update_one(action.uuid, {"role": CompanyRole.ADMIN})

        return {"message": "User assigned as admin successfully"}

    async def remove_admin(self, company_uuid: UUID, user_uuid: UUID, owner_uuid: UUID):
        company = await self.company_repository.get_one_by_params_or_404(uuid=company_uuid)

        if company.owner_uuid != owner_uuid:
            raise UserPermissionDenied()

        action = await self.action_repository.get_one_by_params_or_404(
            company_uuid=company_uuid,
            user_uuid=user_uuid
        )

        await self.action_repository.update_one(action.uuid, {"role": CompanyRole.MEMBER})

        return {"message": "User removed from admin successfully"}

    async def get_company_admin(self, company_uuid: UUID, owner_uuid: UUID, skip: int = 1, limit: int = 10) -> dict:
        company = await self.company_repository.get_one_by_params_or_404(uuid=company_uuid)

        if company.owner_uuid != owner_uuid:
            raise UserPermissionDenied()

        users = await self.action_repository.get_many(
            company_uuid=company_uuid,
            role=CompanyRole.ADMIN,
            skip=skip,
            limit=limit
        )

        return {"users": users}
