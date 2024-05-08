import uuid
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from app.model.base_models import Base
from sqlalchemy.sql import func
from sqlalchemy.dialects.postgresql import UUID


class Notification(Base):
    __tablename__ = 'notifications'

    uuid = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_uuid = Column(UUID, ForeignKey('users.uuid', ondelete='CASCADE'))
    text = Column(String)
    status = Column(String)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
