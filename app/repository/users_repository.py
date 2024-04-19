from app.repository.base_repository import BaseRepository
from app.model.user import User


class UserRepository(BaseRepository[User]):
    def __init__(self, session):
        super().__init__(session=session, model=User)
