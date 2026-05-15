from uuid import UUID

from sqlalchemy.orm import Session

from app.models.conversation_message import ConversationMessage


class MessageRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(
        self,
        session_id: UUID,
        role: str,
        content: str,
        message_type: str = "text",
        metadata_json: dict | None = None,
        riasec_signal: dict | None = None,
    ) -> ConversationMessage:
        message = ConversationMessage(
            session_id=session_id,
            role=role,
            content=content,
            message_type=message_type,
            metadata_json=metadata_json,
            riasec_signal=riasec_signal,
        )

        self.db.add(message)
        self.db.commit()
        self.db.refresh(message)

        return message

    def list_by_session(self, session_id: UUID) -> list[ConversationMessage]:
        return (
            self.db.query(ConversationMessage)
            .filter(ConversationMessage.session_id == session_id)
            .order_by(ConversationMessage.created_at.asc())
            .all()
        )

    def update_signal(
        self,
        message: ConversationMessage,
        riasec_signal: dict,
    ) -> ConversationMessage:
        message.riasec_signal = riasec_signal
        self.db.add(message)
        self.db.commit()
        self.db.refresh(message)

        return message
