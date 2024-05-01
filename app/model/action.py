import uuid

from sqlalchemy import Column, ForeignKey, DateTime, Enum
from sqlalchemy.dialects.postgresql import UUID


from sqlalchemy.sql import func

from app.utils.enum import CompanyRole
from app.model.base_models import BaseClass


class Action(BaseClass):
    __tablename__ = 'actions'

    uuid = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    company_uuid = Column(UUID, ForeignKey('companies.uuid', ondelete='CASCADE'))
    user_uuid = Column(UUID, ForeignKey('users.uuid', ondelete='CASCADE'))
    role = Column(Enum(CompanyRole), index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
