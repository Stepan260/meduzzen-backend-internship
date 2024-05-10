from uuid import UUID

from pydantic import BaseModel
from typing import Optional, List


class CompanyBase(BaseModel):
    company_name: str
    description: str
    is_visible: bool


class CompanyUpdate(BaseModel):
    company_name: Optional[str] = None
    description: Optional[str] = None
    is_visible: Optional[bool] = None


class CompanyCreate(CompanyBase):
    pass


class FullCompany(BaseModel):
    uuid: UUID
    owner_uuid: UUID
    company_name: str
    description: str
    is_visible: bool


class CompaniesListResponse(BaseModel):
    companies: List[FullCompany]


class Companies(BaseModel):
    owner_uuid: UUID
    company_name: str
    description: str
    is_visible: bool