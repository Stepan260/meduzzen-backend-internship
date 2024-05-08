from app.repository.base_repository import BaseRepository
from app.model.notification import Notification


class NotificationRepository(BaseRepository[Notification]):
    def __init__(self, session):
        super().__init__(session=session, model=Notification)
