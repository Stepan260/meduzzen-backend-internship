from enum import Enum


class CompanyRole(str, Enum):
    ADMIN = 'admin'
    MEMBER = 'member'
    OWNER = 'owner'
    INVITED = 'invited'
    REQUESTED = 'requested'
    DECLINED = 'declined'
    BLOCKED = 'blocked'


class ActionType(str, Enum):
    DECLINE = 'decline',
    ACCEPT = 'accept'
