from app.repository.base_repository import BaseRepository
from app.model.quizzes import Quiz


class QuizRepository(BaseRepository[Quiz]):
    def __init__(self, session):
        super().__init__(session=session, model=Quiz)
