from app.repository.base_repository import BaseRepository
from app.model.action import Action


class RequestedRepository(BaseRepository[Action]):
    def __init__(self, session):
        super().__init__(session=session, model=Action)
