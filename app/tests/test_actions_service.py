import pytest

from uuid import UUID

from app.service.action_service import ActionsService
from app.service.сustom_exception import UserPermissionDenied
from app.utils.enum import CompanyRole


@pytest.mark.asyncio
async def test_remove_user_successful(db_session, mock_action_repository, mock_company_repository,
                                      mock_user_repository):
    service = ActionsService(db_session, mock_action_repository, mock_company_repository, mock_user_repository)
    company_uuid = UUID("550e8400-e29b-41d4-a716-446655440000")
    user_uuid = UUID("550e8400-e29b-41d4-a716-446655440001")
    owner_uuid = UUID("550e8400-e29b-41d4-a716-446655440002")

    mock_action_repository.get_one = {
        "company_uuid": company_uuid,
        "user_uuid": user_uuid,
        "role": CompanyRole.MEMBER
    }

    result = await service.remove_user(company_uuid, user_uuid, owner_uuid)

    assert result == {"message": "User removed successfully from the company"}


@pytest.mark.asyncio
async def test_remove_user_successful(db_session, mock_action_repository, mock_company_repository,
                                      mock_user_repository):
    company_uuid = UUID("550e8400-e29b-41d4-a716-446655440000")
    user_uuid = UUID("550e8400-e29b-41d4-a716-446655440001")

    mock_action_repository.get_one = {
        "company_uuid": company_uuid,
        "user_uuid": user_uuid,
        "role": CompanyRole.MEMBER
    }


@pytest.mark.asyncio
async def test_remove_user_permission_denied(db_session, mock_action_repository, mock_company_repository,
                                             mock_user_repository):
    service = ActionsService(db_session, mock_action_repository, mock_company_repository, mock_user_repository)
    company_uuid = UUID("550e8400-e29b-41d4-a716-446655440000")
    user_uuid = UUID("550e8400-e29b-41d4-a716-446655440001")
    owner_uuid = UUID("550e8400-e29b-41d4-a716-446655440002")

    # Act and Assert
    with pytest.raises(UserPermissionDenied):
        await service.remove_user(company_uuid, user_uuid, owner_uuid)
