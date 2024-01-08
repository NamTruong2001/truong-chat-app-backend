from model import (
    ConversationModel,
    ParticipantModel,
    UserModel,
    MessageModel,
    AttachmentModel,
)
from schemas import MessageDTO, Attachment, ConversationDTO, UserDTO
from schemas.participant import ParticipantDTO


def map_user(user: UserModel):
    return (
        UserDTO(
            id=user.id,
            username=user.username,
            first_name=user.first_name,
            last_name=user.last_name,
            email=user.email,
        )
        if user is not None
        else None
    )


def map_message(message: MessageModel):
    message_attachment: AttachmentModel = message.attachment
    return MessageDTO(
        id=str(message.id),
        sender_id=message.sender_id,
        message_type=message.message_type,
        message=message.message,
        created_at=message.created_at,
        conversation_id=message.conversation_id,
        user=map_user(message.user),
        attachment=Attachment(
            file_name=message_attachment.file_name,
            original_file_name=message_attachment.original_file_name,
            azure_file_url=None,
        )
        if message_attachment is not None
        else None,
    )


def map_participant(participant: ParticipantModel):
    return ParticipantDTO(
        id=participant.id,
        created_at=participant.created_at,
        updated_at=participant.updated_at,
        user=map_user(participant.user),
        type=participant.type,
    )


def map_conversation(conversation: ConversationModel):
    return ConversationDTO(
        id=conversation.id,
        title=conversation.title,
        creator_id=conversation.creator_id,
        created_at=conversation.created_at,
        updated_at=conversation.updated_at,
        type=conversation.type,
        messages=[map_message(message) for message in conversation.messages],
        participants=[
            map_participant(participant) for participant in conversation.participants
        ],
    )
