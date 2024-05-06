from typing import List

from click import UUID
from select import select

from app.repository.base_repository import BaseRepository
from app.model.quizzes import Result


class ResultRepository(BaseRepository[Result]):
    def __init__(self, session):
        super().__init__(session=session, model=Result)
