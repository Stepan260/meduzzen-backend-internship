from app.repository.base_repository import BaseRepository
from app.model.user import Users


class UserRepository(BaseRepository):
    def __init__(self, session):
        super().__init__(session=session, model=Users)
