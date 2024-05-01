from datetime import datetime
from typing import List
from uuid import UUID

from pydantic import BaseModel

from app.utils.enum import CompanyRole


class ActionBaseSchema(BaseModel):
    user_uuid: UUID
    uuid: UUID


class AdminUser(BaseModel):
    user_uuid: UUID
    company_uuid: UUID


class ActionSchema(ActionBaseSchema):
    user_uuid: UUID
    company_uuid: UUID


class BaseInviteSchema(BaseModel):
    user_uuid: UUID
    company_uuid: UUID


class BaseRequestSchema(BaseModel):
    company_uuid: UUID


class ActionRequestSchema(BaseRequestSchema):
    user_uuid: UUID


class InviteSchema(BaseModel):
    uuid: UUID
    company_uuid: UUID
    user_uuid: UUID
    role: CompanyRole
    created_at: datetime
    updated_at: datetime


class AcceptRequestSchema(BaseModel):
    action_uuid: UUID


class Request(BaseModel):
    uuid: UUID
    company_uuid: UUID
    user_uuid: UUID


class RequestSchema(BaseModel):
    companies: List[Request]


class UserRequestsResponse(BaseModel):
    requests: List[ActionSchema]


class UserInvitesResponse(BaseModel):
    invites: List[ActionSchema]


class CompanyUsersResponse(BaseModel):
    users: List[ActionSchema]


class AdminUsersResponse(BaseModel):
    users: List[AdminUser]
