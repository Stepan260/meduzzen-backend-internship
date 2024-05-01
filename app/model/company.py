import uuid

from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy import Column, String, Boolean, ForeignKey

from app.model.base_models import BaseClass


class Company(BaseClass):
    __tablename__ = "companies"

    uuid = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    company_name = Column(String, unique=True, index=True)
    owner_uuid = Column(UUID, ForeignKey("users.uuid", ondelete='CASCADE'))
    description = Column(String)
    is_visible = Column(Boolean)
