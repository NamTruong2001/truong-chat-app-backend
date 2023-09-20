from enum import Enum

class MessageEnum(str, Enum):
    image = "image"
    video = "video"
    text = "text"