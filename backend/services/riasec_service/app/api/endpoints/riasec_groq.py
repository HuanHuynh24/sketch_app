from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional, Dict, List
from app.core.database import get_db
from app.core.security import get_current_user_id
from app.schemas.riasec import (
    ResultResponse, ScoreDetail,
    UnifiedChatRequest, UnifiedChatResponse,
)
from app.repositories.riasec_session_repo import riasec_session_repo
from app.repositories.conversation_message_repo import conversation_message_repo
from app.services.llm_groq_service import generate_greeting, generate_question, extract_signal
from app.services.scoring_groq_service import calc_confidence, should_stop, run_final_scoring_job, update_user_scores
import logging

logger = logging.getLogger(__name__)

router = APIRouter()



# ---------------------------------------------------------------------------
# POST /chat — API ĐƠN NHẤT QUÁN TOÀN BỘ LUỒNG (1-API Flow) 🌟
# ---------------------------------------------------------------------------
@router.post("/chat", response_model=UnifiedChatResponse)
async def unified_chat(
    data: UnifiedChatRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    user_id: str = Depends(get_current_user_id),
):
    student_id = data.student_id
    answer = data.answer.strip() if data.answer else None

    # Ưu tiên sử dụng student_id giải mã trực tiếp từ JWT (được lưu tại user_id)
    # khi AUTH_ENABLED = True để đảm bảo độ tin cậy bảo mật tuyệt đối, loại bỏ lỗi gửi nhầm student_id từ body.
    from app.core.config import settings
    if settings.AUTH_ENABLED and user_id and user_id != "test_user_id":
        try:
            import uuid
            uuid.UUID(user_id)
            student_id = user_id
        except ValueError:
            pass

    if not student_id:
        raise HTTPException(status_code=400, detail="student_id is required")



    # 1. Tìm kiếm session đang hoạt động ("in_progress") của học sinh này
    session = riasec_session_repo.get_active_session_by_student_id(db, student_id)


    # TRƯỜNG HỢP A: BẮT ĐẦU HOẶC KHÔI PHỤC PHIÊN CHAT
    if not session:
        # Tạo mới session
        session = riasec_session_repo.create(db, student_id)
        
        # Sinh câu hỏi đầu tiên đồng bộ qua Groq
        first_q = await generate_greeting()

        # Lưu tin nhắn đầu tiên của assistant vào DB
        conversation_message_repo.create(
            db=db,
            session_id=session.session_id,
            role="assistant",
            content=first_q,
            sequence_no=1,
        )

        return {
            "status": "in_progress",
            "session_id": str(session.session_id),
            "question_no": 1,
            "message": first_q,
            "confidence": 0.0,
            "scores": {"R": 0, "I": 0, "A": 0, "S": 0, "E": 0, "C": 0}
        }

    # Nếu có session nhưng người dùng gửi yêu cầu trống (khởi động lại hoặc vào lại trang) -> Trả về câu hỏi hiện tại
    if not answer:
        last_msg = conversation_message_repo.get_last_assistant_message(db, session.session_id)
        msg_text = last_msg.content if last_msg else "Chào em, chúng ta bắt đầu làm khảo sát nhé!"
        return {
            "status": "in_progress",
            "session_id": str(session.session_id),
            "question_no": session.question_count,
            "message": msg_text,
            "confidence": session.confidence,
            "scores": session.current_scores or {"R": 0, "I": 0, "A": 0, "S": 0, "E": 0, "C": 0}
        }

    # TRƯỜNG HỢP B: NGƯỜI DÙNG GỬI CÂU TRẢ LỜI (TIẾP TỤC HỘI THOẠI)
    # Lưu tin nhắn câu trả lời của user
    seq = session.question_count * 2
    conversation_message_repo.create(
        db=db,
        session_id=session.session_id,
        role="user",
        content=answer,
        sequence_no=seq,
    )

    # Lấy câu hỏi assistant gần nhất làm context trích xuất tín hiệu
    last_assistant_msg = conversation_message_repo.get_last_assistant_message(db, session.session_id)
    question_context = last_assistant_msg.content if last_assistant_msg else ""

    # Trích xuất tín hiệu RIASEC qua Groq
    signal_data = await extract_signal(question_context, answer)
    signals = signal_data.get("signals", {})

    # Tính điểm số lũy kế
    current_scores = session.current_scores or {"R": 0, "I": 0, "A": 0, "S": 0, "E": 0, "C": 0}
    groups_asked = session.groups_asked or {"R": 0, "I": 0, "A": 0, "S": 0, "E": 0, "C": 0}

    for k, v in signals.items():
        if k in current_scores:
            current_scores[k] += v
            if v > 0:
                groups_asked[k] = groups_asked.get(k, 0) + 1

    # Tính độ tin cậy confidence
    conf = calc_confidence(current_scores, groups_asked, session.question_count)

    # Cập nhật tạm thời điểm session
    riasec_session_repo.update_session(
        db=db,
        session=session,
        current_scores=current_scores,
        groups_asked=groups_asked,
        confidence=conf,
    )

    # Đồng bộ điểm tạm thời qua API nội bộ dưới nền
    background_tasks.add_task(
        update_user_scores,
        session.student_id,
        current_scores.copy(),
        conf,
    )

    # Kiểm tra điều kiện dừng (6-8 câu lý tưởng, tối đa 10 câu)
    if should_stop(conf, current_scores, session.question_count):
        # Đánh dấu hoàn thành
        riasec_session_repo.complete_session(db, session)

        # Chạy tác vụ nền để Groq phân tích báo cáo chi tiết cuối cùng
        background_tasks.add_task(
            run_final_scoring_job,
            str(session.session_id),
            session.student_id,
        )

        return {
            "status": "completed",
            "session_id": str(session.session_id),
            "question_no": session.question_count,
            "message": "Cảm ơn em đã hoàn thành bài trắc nghiệm hướng nghiệp RIASEC! Kết quả phân tích sâu chi tiết và gợi ý ngành học từ AI đang được cập nhật vào hồ sơ của em.",
            "confidence": conf,
            "scores": current_scores
        }

    # Tăng số câu hỏi
    session.question_count += 1
    riasec_session_repo.update_session(
        db=db,
        session=session,
        current_scores=current_scores,
        groups_asked=groups_asked,
        confidence=conf,
        question_count=session.question_count
    )

    # Tìm các nhóm cần khảo sát thêm
    target_groups = sorted(
        current_scores.keys(),
        key=lambda k: (current_scores[k], groups_asked.get(k, 0)),
    )[:2]
    saturated = [k for k, v in groups_asked.items() if v >= 3]

    target_counts = conversation_message_repo.get_target_counts_by_session_id(db, session.session_id)
    history = conversation_message_repo.get_history_by_session_id(db, session.session_id)

    # Sinh câu hỏi mới qua Groq
    next_q = await generate_question(
        session.question_count, target_groups, saturated, history,
        groups_asked=target_counts,
    )

    # Lưu câu hỏi của assistant mới vào DB
    primary_target = target_groups[0] if target_groups else None
    conversation_message_repo.create(
        db=db,
        session_id=session.session_id,
        role="assistant",
        content=next_q,
        riasec_target=primary_target,
        sequence_no=session.question_count * 2 - 1,
    )

    return {
        "status": "in_progress",
        "session_id": str(session.session_id),
        "question_no": session.question_count,
        "message": next_q,
        "confidence": conf,
        "scores": current_scores
    }


# ---------------------------------------------------------------------------
# CÁC API TRUY VẤN VẪN ĐƯỢC GIỮ LẠI ĐỂ TƯƠNG THÍCH HOÀN TOÀN (Backward Compatibility)
# ---------------------------------------------------------------------------

# ---------------------------------------------------------------------------
# API TRUY VẤN KẾT QUẢ ĐÃ ĐƯỢC TỐI ƯU HÓA (Senior Architecture)
# ---------------------------------------------------------------------------

@router.get("/sessions/{session_id}/result", response_model=ResultResponse)
async def get_session_result(
    session_id: str,
    db: Session = Depends(get_db),
    user_id: str = Depends(get_current_user_id),
):
    """
    Lấy kết quả RIASEC chi tiết của session.
    Các trường riasec_code, top_groups, confidence, reasoning, suggested_majors được lấy từ bảng users
    thông qua API nội bộ gọi sang profile_service để đảm bảo dữ liệu hiển thị chính xác nhất.
    """
    import httpx
    from app.core.config import settings

    session = riasec_session_repo.get_by_id(db, session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    if session.status != "completed":
        raise HTTPException(
            status_code=400,
            detail=f"Session chưa hoàn thành (status: {session.status})",
        )

    # Lấy thông tin chi tiết của học sinh từ profile_service qua API nội bộ
    user_data = {}
    try:
        url = f"{settings.PROFILE_SERVICE_URL}/api/profile/internal/users/{session.student_id}"
        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.get(url)
            if resp.status_code == 200:
                user_data = resp.json()
            else:
                logger.error(f"[GROQ FLOW] Failed to fetch internal user data for result: {resp.text}")
    except Exception as e:
        logger.error(f"[GROQ FLOW] Error calling profile_service for user result: {e}")

    # Nếu có dữ liệu từ bảng users, dùng dữ liệu đó. Ngược lại dùng fallback từ session
    riasec_code = user_data.get("riasec_code")
    top_groups = user_data.get("top_groups")
    confidence = user_data.get("confidence") if user_data.get("confidence") is not None else session.confidence
    reasoning = user_data.get("reasoning")
    suggested_majors = user_data.get("suggested_majors")

    # Điểm số (ưu tiên từ bảng user nếu có, fallback từ session)
    scores = session.current_scores or {}
    if user_data:
        scores = {
            "R": user_data.get("score_R", 0.0),
            "I": user_data.get("score_I", 0.0),
            "A": user_data.get("score_A", 0.0),
            "S": user_data.get("score_S", 0.0),
            "E": user_data.get("score_E", 0.0),
            "C": user_data.get("score_C", 0.0),
        }

    return {
        "session_id": str(session.session_id),
        "status": session.status,
        "scores": ScoreDetail(
            R=scores.get("R", 0.0),
            I=scores.get("I", 0.0),
            A=scores.get("A", 0.0),
            S=scores.get("S", 0.0),
            E=scores.get("E", 0.0),
            C=scores.get("C", 0.0),
        ),
        "riasec_code": riasec_code,
        "top_groups": top_groups,
        "confidence": confidence,
        "reasoning": reasoning,
        "suggested_majors": suggested_majors,
    }

