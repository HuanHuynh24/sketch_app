from sqlalchemy.orm import Session
from sqlalchemy import func
from app.models.conversation_message import ConversationMessage

class ConversationMessageRepository:
    def create(self, db: Session, session_id: str, role: str, content: str, sequence_no: int, riasec_target: str = None) -> ConversationMessage:
        msg = ConversationMessage(
            session_id=session_id,
            role=role,
            content=content,
            sequence_no=sequence_no,
            riasec_target=riasec_target,
        )
        db.add(msg)
        db.commit()
        db.refresh(msg)
        return msg

    def get_last_assistant_message(self, db: Session, session_id: str) -> ConversationMessage | None:
        return (
            db.query(ConversationMessage)
            .filter(
                ConversationMessage.session_id == session_id,
                ConversationMessage.role == "assistant",
            )
            .order_by(ConversationMessage.sequence_no.desc())
            .first()
        )

    def get_target_counts_by_session_id(self, db: Session, session_id: str) -> dict:
        target_counts = dict(
            db.query(ConversationMessage.riasec_target, func.count())
            .filter(
                ConversationMessage.session_id == session_id,
                ConversationMessage.riasec_target.isnot(None),
            )
            .group_by(ConversationMessage.riasec_target)
            .all()
        )
        return target_counts

    def get_history_by_session_id(self, db: Session, session_id: str) -> list[ConversationMessage]:
        return (
            db.query(ConversationMessage)
            .filter(ConversationMessage.session_id == session_id)
            .order_by(ConversationMessage.sequence_no)
            .all()
        )

conversation_message_repo = ConversationMessageRepository()
