import pytest
from uuid import UUID

from app.schemas.company import CompanyCreate, Companies
from app.service.company_service import CompanyService


@pytest.mark.asyncio
async def test_create_company_successful(db_session, mock_company_repository):
    service = CompanyService(db_session, mock_company_repository)
    company_create = CompanyCreate(
        company_name="New Company",
        description="A new company description",
        is_visible=True
    )
    owner_uuid = UUID("550e8400-e29b-41d4-a716-446655440000")

    mock_company_repository.get_one.return_value = None

    expected_company = Companies(
        company_name="New Company",
        description="A new company description",
        is_visible=True,
        owner_uuid=owner_uuid
    )

    mock_company_repository.create_one.return_value = expected_company

    company = await service.create_company(company_create, owner_uuid)

    assert company.company_name == "New Company"
    assert company.description == "A new company description"
    assert company.is_visible is True
    assert company.owner_uuid == owner_uuid
