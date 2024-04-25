from uuid import UUID
from fastapi import APIRouter, Depends, Query, Response, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.schemas.company import FullCompany, CompanyBase, CompaniesListResponse, CompanyCreate, CompanyUpdate
from app.schemas.user import UserDetail
from app.service.auth_service import AuthService
from app.service.company_service import CompanyService
from app.db.postgres import get_session

router = APIRouter(tags=["Company"], prefix='/company')


async def get_company_service(session: AsyncSession = Depends(get_session)) -> CompanyService:
    from app.repository.company_repository import CompanyRepository
    company_repository = CompanyRepository(session)
    return CompanyService(session=session, repository=company_repository)


@router.get("/{company_id}", response_model=FullCompany)
async def get_company_by_id(company_id: UUID, company_service: CompanyService = Depends(get_company_service),
                            current_user: UserDetail = Depends(AuthService.get_current_user)):
    return await company_service.get_company_by_id(company_id)


@router.post("/", response_model=CompanyBase, status_code=201)
async def create_company(company_create: CompanyCreate, company_service: CompanyService = Depends(get_company_service),
                         current_user: UserDetail = Depends(AuthService.get_current_user)):
    owner_uuid = current_user.uuid
    return await company_service.create_company(company_create, owner_uuid)


@router.put("/{company_id}/update_info/", response_model=CompanyBase)
async def update_company(company_uuid: UUID, company_update: CompanyUpdate,
                         company_service: CompanyService = Depends(get_company_service),
                         current_user: UserDetail = Depends(AuthService.get_current_user)):
    owner_uuid = current_user.uuid
    return await company_service.update_company(company_uuid, company_update, owner_uuid)


@router.delete("/{company_id}", response_class=Response, status_code=status.HTTP_204_NO_CONTENT)
async def delete_company(company_uuid: UUID, company_service: CompanyService = Depends(get_company_service),
                         current_user: UserDetail = Depends(AuthService.get_current_user)):
    owner_uuid = current_user.uuid
    await company_service.delete_company(company_uuid, owner_uuid)
    return Response(status_code=204)


@router.get("/", response_model=CompaniesListResponse)
async def get_all_companies(
        company_service: CompanyService = Depends(get_company_service),
        current_user: UserDetail = Depends(AuthService.get_current_user),
        skip: int = 1, limit: int = 10):
    return await company_service.get_all_companies(skip=skip, limit=limit)
