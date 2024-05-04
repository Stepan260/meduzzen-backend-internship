from app.repository.base_repository import BaseRepository
from app.model.quizzes import TestResult


class ResultRepository(BaseRepository[TestResult]):
    def __init__(self, session):
        super().__init__(session=session, model=TestResult)
