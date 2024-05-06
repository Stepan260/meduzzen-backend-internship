from app.repository.base_repository import BaseRepository
from app.model.quizzes import Question


class QuestionRepository(BaseRepository[Question]):
    def __init__(self, session):
        super().__init__(session=session, model=Question)
