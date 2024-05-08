from pydantic import BaseModel
from datetime import datetime
from uuid import UUID


class NotificationSchema(BaseModel):
    uuid: UUID
    user_uuid: UUID
    text: str
    status: str
    created_at: datetime


class NotificationUpdateSchema(BaseModel):
    status: str

