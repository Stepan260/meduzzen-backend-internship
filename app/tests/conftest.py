import pytest
from fastapi.testclient import TestClient
from app.main import app
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.postgres import get_session
from unittest.mock import MagicMock
from app.repository.action_repository import ActionRepository
from app.repository.company_repository import CompanyRepository
from app.repository.users_repository import UserRepository
from app.repository.invites_repository import InvitesRepository
from app.repository.quizzes_repository import QuizRepository
from app.repository.question_repository import QuestionRepository
from app.repository.result_repository import ResultRepository


@pytest.fixture
def client():
    return TestClient(app)


@pytest.fixture
async def db_session():
    session: AsyncSession = await get_session()
    yield session
    await session.close()


@pytest.fixture
def mock_action_repository():
    return MagicMock(spec=ActionRepository)


@pytest.fixture
def mock_company_repository():
    return MagicMock(spec=CompanyRepository)


@pytest.fixture()
def mock_user_repository():
    return MagicMock(spec=UserRepository)


@pytest.fixture
def mock_invites_repository():
    return MagicMock(spec=InvitesRepository)


@pytest.fixture
def mock_quiz_repository():
    return MagicMock(spec=QuizRepository)


@pytest.fixture
def mock_question_repository():
    return MagicMock(spec=QuestionRepository)


@pytest.fixture
def mock_result_repository():
    return MagicMock(spec=ResultRepository)



