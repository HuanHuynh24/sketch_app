from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.security import get_current_user_id
from app.schemas.riasec import (
    SessionCreate, SessionResponse,
    MessageCreate, MessageResponse,
    SessionAbandonResponse,
    HistoryResponse, MessageItem,
    ResultResponse, ScoreDetail,
)
from app.models.riasec_session import RiasecSession
from app.models.conversation_message import ConversationMessage
from app.services.llm_service import generate_greeting, generate_question, extract_signal
from app.services.scoring_service import calc_confidence, should_stop, run_final_scoring_job, update_user_scores
from datetime import datetime

router = APIRouter()


# ---------------------------------------------------------------------------
# POST /sessions — Tạo session mới + lời chào + tình huống đầu tiên
# ---------------------------------------------------------------------------
@router.post("/sessions", response_model=SessionResponse)
async def create_session(
    data: SessionCreate,
    db: Session = Depends(get_db),
    user_id: str = Depends(get_current_user_id),
):
    student_id = data.student_id

    # Kiểm tra session in_progress đã tồn tại
    existing = (
        db.query(RiasecSession)
        .filter(
            RiasecSession.student_id == student_id,
            RiasecSession.status == "in_progress",
        )
        .first()
    )
    if existing:
        raise HTTPException(status_code=409, detail="Đã có session đang diễn ra")

    # Tạo session mới
    new_session = RiasecSession(student_id=student_id, question_count=1)
    db.add(new_session)
    db.commit()
    db.refresh(new_session)

    # Gọi Gemini tạo lời chào + tình huống đầu tiên
    first_q = await generate_greeting()

    # Lưu tin nhắn đầu tiên của assistant
    msg = ConversationMessage(
        session_id=new_session.session_id,
        role="assistant",
        content=first_q,
        sequence_no=1,
    )
    db.add(msg)
    db.commit()

    return {
        "session_id": str(new_session.session_id),
        "first_question": first_q,
        "question_no": 1,
        "status": "in_progress",
    }


# ---------------------------------------------------------------------------
# POST /sessions/{id}/messages — Gửi câu trả lời, nhận tình huống tiếp
# ---------------------------------------------------------------------------
@router.post("/sessions/{session_id}/messages", response_model=MessageResponse)
async def send_message(
    session_id: str,
    data: MessageCreate,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    user_id: str = Depends(get_current_user_id),
):
    # Validate input
    if not data.answer.strip():
        raise HTTPException(status_code=400, detail="Câu trả lời không được để trống")

    # Lấy session
    session = (
        db.query(RiasecSession)
        .filter(RiasecSession.session_id == session_id)
        .first()
    )
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    if session.status == "completed":
        raise HTTPException(status_code=409, detail="Session đã hoàn thành")
    if session.status == "abandoned":
        raise HTTPException(status_code=409, detail="Session đã bị hủy")

    # Lưu tin nhắn user
    seq = session.question_count * 2
    user_msg = ConversationMessage(
        session_id=session.session_id,
        role="user",
        content=data.answer,
        sequence_no=seq,
    )
    db.add(user_msg)

    # Lấy câu hỏi gốc (tin nhắn assistant gần nhất) để cung cấp context
    last_assistant_msg = (
        db.query(ConversationMessage)
        .filter(
            ConversationMessage.session_id == session_id,
            ConversationMessage.role == "assistant",
        )
        .order_by(ConversationMessage.sequence_no.desc())
        .first()
    )
    question_context = last_assistant_msg.content if last_assistant_msg else ""

    # Gọi Gemini phân tích tín hiệu RIASEC — gửi kèm câu hỏi gốc
    signal_data = await extract_signal(question_context, data.answer)
    signals = signal_data.get("signals", {})

    # Cập nhật scores tích lũy
    current_scores = session.current_scores or {"R": 0, "I": 0, "A": 0, "S": 0, "E": 0, "C": 0}
    groups_asked = session.groups_asked or {"R": 0, "I": 0, "A": 0, "S": 0, "E": 0, "C": 0}

    for k, v in signals.items():
        if k in current_scores:
            current_scores[k] += v
            if v > 0:
                groups_asked[k] = groups_asked.get(k, 0) + 1

    # Gán lại .copy() để SQLAlchemy detect thay đổi JSONB
    session.current_scores = current_scores.copy()
    session.groups_asked = groups_asked.copy()

    # Tính confidence
    conf = calc_confidence(current_scores, groups_asked, session.question_count)
    session.confidence = conf

    # ★ Cập nhật điểm vào bảng users SAU MỖI câu trả lời
    background_tasks.add_task(
        update_user_scores,
        session.student_id,
        current_scores.copy(),
        conf,
    )

    # Kiểm tra điều kiện dừng
    if should_stop(conf, current_scores, session.question_count):
        session.status = "completed"
        session.completed_at = datetime.utcnow()
        db.commit()

        # Chạy background job Gemini phân tích chi tiết (reasoning, suggested_majors)
        background_tasks.add_task(
            run_final_scoring_job,
            str(session.session_id),
            session.student_id,
        )
        return {"status": "completed", "confidence": conf, "scores": current_scores}

    # Chưa dừng → tạo tình huống tiếp theo
    session.question_count += 1
    db.commit()

    # Xác định nhóm cần khai thác — ưu tiên nhóm ĐIỂM THẤP NHẤT
    # Tie-break: nhóm ít được hỏi hơn sẽ được ưu tiên
    target_groups = sorted(
        current_scores.keys(),
        key=lambda k: (current_scores[k], groups_asked.get(k, 0)),
    )[:2]
    saturated = [k for k, v in groups_asked.items() if v >= 4]

    # Đếm số lần mỗi nhóm đã được target → để chọn tình huống chưa dùng
    from sqlalchemy import func
    target_counts = dict(
        db.query(ConversationMessage.riasec_target, func.count())
        .filter(
            ConversationMessage.session_id == session_id,
            ConversationMessage.riasec_target.isnot(None),
        )
        .group_by(ConversationMessage.riasec_target)
        .all()
    )

    # Lấy toàn bộ history để Gemini "nhớ" cuộc hội thoại
    history = (
        db.query(ConversationMessage)
        .filter(ConversationMessage.session_id == session_id)
        .order_by(ConversationMessage.sequence_no)
        .all()
    )
    next_q = await generate_question(
        session.question_count, target_groups, saturated, history,
        groups_asked=target_counts,
    )

    # Lưu tin nhắn assistant mới — ghi nhận nhóm RIASEC mục tiêu
    primary_target = target_groups[0] if target_groups else None
    ast_msg = ConversationMessage(
        session_id=session.session_id,
        role="assistant",
        content=next_q,
        riasec_target=primary_target,
        sequence_no=session.question_count * 2 - 1,
    )
    db.add(ast_msg)
    db.commit()

    return {
        "status": "in_progress",
        "next_question": next_q,
        "question_no": session.question_count,
        "confidence": conf,
        "scores": current_scores,
    }


# ---------------------------------------------------------------------------
# GET /sessions/{id} — Xem trạng thái session
# ---------------------------------------------------------------------------
@router.get("/sessions/{session_id}", response_model=SessionResponse)
def get_session(
    session_id: str,
    db: Session = Depends(get_db),
    user_id: str = Depends(get_current_user_id),
):
    session = (
        db.query(RiasecSession)
        .filter(RiasecSession.session_id == session_id)
        .first()
    )
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    return {
        "session_id": str(session.session_id),
        "status": session.status,
        "question_count": session.question_count,
        "confidence": session.confidence,
    }


# ---------------------------------------------------------------------------
# GET /sessions/{id}/history — Xem lịch sử hội thoại
# ---------------------------------------------------------------------------
@router.get("/sessions/{session_id}/history", response_model=HistoryResponse)
def get_session_history(
    session_id: str,
    db: Session = Depends(get_db),
    user_id: str = Depends(get_current_user_id),
):
    session = (
        db.query(RiasecSession)
        .filter(RiasecSession.session_id == session_id)
        .first()
    )
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    messages = (
        db.query(ConversationMessage)
        .filter(ConversationMessage.session_id == session_id)
        .order_by(ConversationMessage.sequence_no)
        .all()
    )

    return {
        "session_id": str(session.session_id),
        "messages": [
            MessageItem(
                role=m.role,
                content=m.content,
                sequence_no=m.sequence_no,
            )
            for m in messages
        ],
        "question_count": session.question_count,
        "status": session.status,
    }


# ---------------------------------------------------------------------------
# GET /sessions/{id}/result — Xem kết quả RIASEC (sau khi completed)
# ---------------------------------------------------------------------------
@router.get("/sessions/{session_id}/result", response_model=ResultResponse)
def get_session_result(
    session_id: str,
    db: Session = Depends(get_db),
    user_id: str = Depends(get_current_user_id),
):
    session = (
        db.query(RiasecSession)
        .filter(RiasecSession.session_id == session_id)
        .first()
    )
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    if session.status != "completed":
        raise HTTPException(
            status_code=400,
            detail=f"Session chưa hoàn thành (status: {session.status})",
        )

    # Lấy scores từ session.current_scores
    scores = session.current_scores or {}

    return {
        "session_id": str(session.session_id),
        "status": session.status,
        "scores": ScoreDetail(
            R=scores.get("R", 0),
            I=scores.get("I", 0),
            A=scores.get("A", 0),
            S=scores.get("S", 0),
            E=scores.get("E", 0),
            C=scores.get("C", 0),
        ),
        "confidence": session.confidence,
    }


# ---------------------------------------------------------------------------
# PATCH /sessions/{id}/abandon — Bỏ session
# ---------------------------------------------------------------------------
@router.patch("/sessions/{session_id}/abandon", response_model=SessionAbandonResponse)
def abandon_session(
    session_id: str,
    db: Session = Depends(get_db),
    user_id: str = Depends(get_current_user_id),
):
    session = (
        db.query(RiasecSession)
        .filter(RiasecSession.session_id == session_id)
        .first()
    )
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    if session.status == "completed":
        raise HTTPException(status_code=409, detail="Session đã hoàn thành, không thể hủy")
    if session.status == "abandoned":
        raise HTTPException(status_code=409, detail="Session đã bị hủy trước đó")

    session.status = "abandoned"
    db.commit()
    return {"session_id": str(session.session_id), "status": "abandoned"}
