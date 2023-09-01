import enum

class ConversationRole(enum.Enum):
    CREATOR = "creator"
    MEMBER = "member"
    TEXT = "text"