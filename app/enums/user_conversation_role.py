from enum import Enum


class UserConversationRole(str, Enum):
    creator = "creator"
    member = "member"
