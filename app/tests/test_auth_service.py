import pytest

from app.schemas.auth import  SignInRequest
from app.service.auth_service import AuthService

@pytest.mark.asyncio
async def test_signup_successful(db_session, mock_user_repository):

    service = AuthService(db_session, mock_user_repository)
    user_create = SignInRequest(email="test@example.com", password="password")

    mock_user_repository.get_one.return_value = None

    result = await service.signup(user_create)

    assert result["access_token"] is not None
    assert result["token_type"] == "bearer"