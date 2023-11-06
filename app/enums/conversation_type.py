from enum import Enum


class ConversationTypeEnum(str, Enum):
    private = "private"
    group = "group"
