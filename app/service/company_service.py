from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession

from app.model.company import Company
from app.repository.company_repository import CompanyRepository

from app.schemas.company import CompanyUpdate, CompanyCreate
from app.service.сustom_exception import UserPermissionDenied, CompanyAlreadyExists, CompanyNotFound


class CompanyService:
    def __init__(self, session: AsyncSession, repository: CompanyRepository):
        self.repository = repository
        self.session = session

    async def create_company(self, company_create: CompanyCreate, owner_uuid: UUID) -> Company:
        existing_company = await self.repository.get_one(
            company_name=company_create.company_name,
            owner_uuid=owner_uuid
        )
        if existing_company:
            raise CompanyAlreadyExists(identifier='company_name')
        return await self.repository.create_one(dict(**company_create.model_dump(), owner_uuid=owner_uuid))

    async def update_company(self, company_uuid: UUID, company_update: CompanyUpdate, owner_uuid: UUID) -> Company:
        company = await self.repository.get_one(uuid=company_uuid)
        if company.owner_uuid != owner_uuid:
            raise UserPermissionDenied()
        return await self.repository.update_one(company_uuid, company_update.model_dump())

    async def delete_company(self, company_uuid: UUID, owner_uuid: UUID) -> None:
        company = await self.repository.get_one(uuid=company_uuid)
        if company.owner_uuid != owner_uuid:
            raise UserPermissionDenied()
        await self.repository.delete_one(company_uuid)

    async def get_all_companies(self, skip: int = 1, limit: int = 10) -> dict:
        companies = await self.repository.get_many(skip=skip, limit=limit)
        return {'companies': companies}

    async def get_company_by_id(self, company_uuid: UUID) -> Company:
        db_company = await self.repository.get_one(uuid=company_uuid)
        if not db_company:
            raise CompanyNotFound(identifier='uuid')
        return db_company
