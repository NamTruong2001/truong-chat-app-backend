from model import ConversationModel, ParticipantModel, UserModel
from schemas import MessageDTO, Attachment, ConversationDTO, UserDTO
from schemas.participant import ParticipantDTO


def map_message(document):
    message_attachment = document["attachment"]
    return MessageDTO(
        id=str(document["_id"]),
        sender_id=document["sender_id"],
        message_type=document["message_type"],
        message=document["message"],
        created_at=document["created_at"],
        conversation_id=document["conversation_id"],
        attachment=Attachment(
            file_name=message_attachment["file_name"],
            original_file_name=message_attachment["original_file_name"],
            azure_file_url=message_attachment["azure_file_url"]
        ) if message_attachment is not None else None
    )

def map_user(user: UserModel):
    return UserDTO(
        id=user.id,
        username=user.username,
        first_name=user.first_name,
        last_name=user.last_name,
        email=user.email
    )

def map_participant(participant: ParticipantModel):
    return ParticipantDTO(
        id=participant.id,
        created_at=participant.created_at,
        updated_at=participant.updated_at,
        user=map_user(participant.user),
        type=participant.type
    )

def map_conversation(conversation: ConversationModel):
    return ConversationDTO(
        id=conversation.id,
        title=conversation.title,
        creator_id=conversation.creator_id,
        created_at=conversation.created_at,
        updated_at=conversation.updated_at,
        type=conversation.type,
        participants=[map_participant(participant) for participant in conversation.participants]
    )