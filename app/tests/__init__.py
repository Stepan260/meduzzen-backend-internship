import pytest
from app.service.action_service import ActionsService
from app.utils.enum import CompanyRole
from app.service.сustom_exception import UserPermissionDenied, UserNotFound


async def test_remove_user_successful(async_session, mock_action_repository, mock_company_repository,
                                      mock_user_repository):

    service = ActionsService(async_session, mock_action_repository, mock_company_repository, mock_user_repository)
    company_uuid = "some-company-uuid"
    user_uuid = "some-user-uuid"
    owner_uuid = "owner-uuid"

    mock_action_repository.get_one.return_value = {
        "company_uuid": company_uuid,
        "user_uuid": user_uuid,
        "role": CompanyRole.MEMBER
    }

    result = await service.remove_user(company_uuid, user_uuid, owner_uuid)

    assert result == {"message": "User removed successfully from the company"}


async def test_remove_user_permission_denied(async_session, mock_action_repository, mock_company_repository,
                                             mock_user_repository):
    service = ActionsService(async_session, mock_action_repository, mock_company_repository, mock_user_repository)
    company_uuid = "some-company-uuid"
    user_uuid = "some-user-uuid"
    owner_uuid = "different-owner-uuid"

    with pytest.raises(UserPermissionDenied):
        await service.remove_user(company_uuid, user_uuid, owner_uuid)
