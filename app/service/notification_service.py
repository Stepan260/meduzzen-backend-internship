from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.repository.notification_repository import NotificationRepository
from app.service.сustom_exception import ObjectNotFound, UserPermissionDenied


class NotificationService:
    def __init__(self,
                 notification_repository: NotificationRepository,
                 session: AsyncSession,
                 ):
        self.notification_repository = notification_repository
        self.session = session,

    async def get_notifications_for_user(self, user_uuid: UUID):
        notifications = await self.notification_repository.get_many(
            skip=1, limit=1000,
            user_uuid=user_uuid
        )
        if not notifications:
            raise ObjectNotFound(identifier=user_uuid, model_name="notifications")

        return notifications

    async def update_notification_status(self, user_uuid: UUID, notification_uuid: UUID):
        notification = await self.notification_repository.get_one_by_params_or_404(uuid=notification_uuid)

        if notification.user_uuid != user_uuid:
            raise UserPermissionDenied()

        await self.notification_repository.update_one(notification.uuid, {"status": 'read'})
