from fastapi import FastAPI, Depends, Request
from sqlalchemy.orm import Session
from pydantic import BaseModel
import uuid
from datetime import datetime

from .database import get_db, engine 
from .models import Base, RiasecSession, ConversationMessage 
from .ai_agent.chatbot import generate_next_question

app = FastAPI(title="RIASEC Service API")

Base.metadata.create_all(bind=engine)

# --- SCHEMA ---
class ChatRequest(BaseModel):
    answer: str

# --- API ENDPOINTS ---

@app.post("/api/v1/riasec/sessions")
def create_session(request: Request, db: Session = Depends(get_db)):
    """[cite: 1] Tạo phiên chat mới và sinh câu hỏi đầu tiên"""
    
    # Lấy student_id do Gateway truyền xuống (Gateway đã check Token)
    student_id_str = request.headers.get("X-User-Id")
    if not student_id_str:
        return {"error": "Unauthorized. Call this via API Gateway."}

    # 1. Khởi tạo phiên mới
    new_session = RiasecSession(
        student_id=uuid.UUID(student_id_str),
        started_at=datetime.utcnow()
    )
    db.add(new_session)
    db.commit()
    db.refresh(new_session)
    
    # 2. Sinh câu hỏi mở đầu bằng Langchain
    first_question = generate_next_question([])
    
    # 3. Lưu câu hỏi của AI vào DB
    ai_msg = ConversationMessage(
        session_id=new_session.session_id,
        role="assistant",
        content=first_question,
        sequence_no=1
    )
    db.add(ai_msg)
    db.commit()
    
    # 4. Trả về đúng format tài liệu yêu cầu[cite: 1]
    return {
        "session_id": new_session.session_id,
        "first_question": first_question,
        "question_no": 1
    }

@app.post("/api/v1/riasec/sessions/{session_id}/messages")
def chat(session_id: str, payload: ChatRequest, db: Session = Depends(get_db)):
    """[cite: 1] Nhận câu trả lời và sinh câu hỏi tiếp theo"""
    
    session = db.query(RiasecSession).filter(RiasecSession.session_id == session_id).first()
    if not session:
        return {"error": "Session không tồn tại"}

    current_seq = session.question_count * 2
    
    # 1. Lưu câu trả lời của User
    user_msg = ConversationMessage(
        session_id=session.session_id,
        role="user",
        content=payload.answer,
        sequence_no=current_seq + 2
    )
    db.add(user_msg)
    
    # 2. Đọc toàn bộ lịch sử để đưa cho Langchain
    all_msgs = db.query(ConversationMessage).filter(
        ConversationMessage.session_id == session.session_id
    ).order_by(ConversationMessage.sequence_no.asc()).all()
    
    chat_history = [{"role": msg.role, "content": msg.content} for msg in all_msgs]
    
    # Thêm câu trả lời mới nhất vào context
    chat_history.append({"role": "user", "content": payload.answer})
    
    # 3. Sinh câu hỏi tiếp theo
    next_question = generate_next_question(chat_history)
    
    # 4. Lưu câu hỏi mới của AI
    ai_msg = ConversationMessage(
        session_id=session.session_id,
        role="assistant",
        content=next_question,
        sequence_no=current_seq + 3
    )
    db.add(ai_msg)
    
    # Cập nhật số câu hỏi
    session.question_count += 1
    db.commit()
    
    return {
        "status": "in_progress",
        "next_question": next_question,
        "question_no": session.question_count + 1,
        "confidence": session.confidence
    }