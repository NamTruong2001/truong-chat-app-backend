from enum import Enum


class MessageEnum(str, Enum):
    image = "image"
    video = "video"
    text = "text"
    voice = "voice"
    document = "document"
    system = "system"
