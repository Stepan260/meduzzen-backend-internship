from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.postgres import get_session
from app.repository.notification_repository import NotificationRepository
from app.schemas.notification import NotificationSchema
from app.schemas.user import UserDetail
from app.service.auth_service import AuthService
from app.service.notification_service import NotificationService

router = APIRouter(tags=["Notification"])


async def get_notification_service(session: AsyncSession = Depends(get_session)) -> NotificationService:
    notification_repository = NotificationRepository(session)

    return NotificationService(
        session=session,
        notification_repository=notification_repository
    )


@router.get("/notifications", response_model=List[NotificationSchema])
async def get_notifications(
        notification_service: NotificationService = Depends(get_notification_service),
        current_user: UserDetail = Depends(AuthService.get_current_user)

):
    user_uuid = current_user.uuid
    return await notification_service.get_notifications_for_user(user_uuid)


@router.patch("/notifications/{notification_uuid}")
async def mark_notification_as_read(
    notification_uuid: UUID,
    current_user: UserDetail = Depends(AuthService.get_current_user),
    notification_service: NotificationService = Depends(get_notification_service)
):
    await notification_service.update_notification_status(current_user.uuid, notification_uuid)
