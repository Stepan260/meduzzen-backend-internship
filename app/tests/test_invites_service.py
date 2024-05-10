from unittest.mock import MagicMock

import pytest
from uuid import UUID

from app.service.invites_service import InvitesService
from app.utils.enum import ActionType, CompanyRole


@pytest.mark.asyncio
async def test_cancel_invite_successful(db_session, mock_invites_repository, mock_company_repository):
    service = InvitesService(db_session, mock_invites_repository, mock_company_repository, MagicMock())
    action_uuid = UUID("550e8400-e29b-41d4-a716-446655440003")
    current_user_uuid = UUID("550e8400-e29b-41d4-a716-446655440002")

    invite = MagicMock(company_uuid=UUID("550e8400-e29b-41d4-a716-446655440000"))
    mock_invites_repository.get_one_by_params_or_404.return_value = invite
    mock_company_repository.get_one_by_params_or_404.return_value = MagicMock(owner_uuid=current_user_uuid)

    await service.cancel_invite(action_uuid, current_user_uuid)

    mock_invites_repository.delete_one.assert_called_once_with(str(action_uuid))


@pytest.mark.asyncio
async def test_accept_or_decline_invite_successful(db_session, mock_invites_repository):
    service = InvitesService(db_session, mock_invites_repository, MagicMock(), MagicMock())
    action_type = ActionType.ACCEPT
    action_uuid = UUID("550e8400-e29b-41d4-a716-446655440003")
    current_user_uuid = UUID("550e8400-e29b-41d4-a716-446655440002")

    invite = MagicMock(user_uuid=current_user_uuid, role=CompanyRole.INVITED)
    mock_invites_repository.get_one_by_params_or_404.return_value = invite

    message = await service.accept_or_decline_invite(action_type, action_uuid, current_user_uuid)

    if action_type == ActionType.ACCEPT:
        assert message["message"] == "Invite accepted successfully, you are now a member of the company"
        mock_invites_repository.update_one.assert_called_once()
    elif action_type == ActionType.DECLINE:
        assert message["message"] == "Invite declined successfully"
        mock_invites_repository.update_one.assert_called_once()
