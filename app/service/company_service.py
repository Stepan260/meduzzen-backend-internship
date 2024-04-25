from http.client import HTTPException
from typing import Optional
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession

from app.repository.company_repository import CompanyRepository

from app.schemas.company import FullCompany, CompanyUpdate, CompaniesListResponse, CompanyCreate
from app.service.сustom_exception import UserPermissionDenied, UserNotFound, CompanyAlreadyExists


class CompanyService:
    def __init__(self, session: AsyncSession, repository: CompanyRepository):
        self.repository = repository
        self.session = session

    async def create_company(self, company_create: CompanyCreate, owner_uuid: UUID) -> FullCompany:
        company_name = company_create.company_name
        description = company_create.description
        is_visible = company_create.is_visible

        existing_company = await self.repository.get_one(company_name=company_name, owner_uuid=owner_uuid)
        if existing_company:
            raise CompanyAlreadyExists()

        company_data = {
            'company_name': company_name,
            'description': description,
            'is_visible': is_visible,
            'owner_uuid': owner_uuid,
        }

        company = await self.repository.create_one(company_data)
        return company

    async def update_company(self, company_uuid: UUID, company_update: CompanyUpdate, owner_uuid: UUID) -> FullCompany:
        company = await self.repository.get_one(uuid=company_uuid)
        if company.owner_uuid != owner_uuid:
            raise UserPermissionDenied()
        updated_company = await self.repository.update_one(company_uuid, company_update.dict())
        return updated_company

    async def delete_company(self, company_uuid: UUID, owner_uuid: UUID) -> None:
        company = await self.repository.get_one(uuid=company_uuid)
        if company.owner_uuid != owner_uuid:
            raise UserPermissionDenied()
        await self.repository.delete_one(company_uuid)

    async def get_all_companies(self, skip: int = 1, limit: int = 10) -> CompaniesListResponse:
        companies = await self.repository.get_many(skip=skip, limit=limit)
        return {'companies': companies}

    async def get_company_by_id(self, company_uuid: UUID) -> Optional[FullCompany]:
        company = await self.repository.get_one(uuid=company_uuid)
        return company
