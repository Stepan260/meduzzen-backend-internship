from app.repository.base_repository import BaseRepository
from app.model.quizzes import Result


class ResultRepository(BaseRepository[Result]):
    def __init__(self, session):
        super().__init__(session=session, model=Result)
