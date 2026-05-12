from sqlalchemy.orm import Session
import httpx
from app.services.llm_groq_service import generate_final_scoring
from app.repositories.conversation_message_repo import conversation_message_repo
from app.core.database import SessionLocal
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)


def calc_confidence(scores: dict, groups_asked: dict, question_no: int) -> float:
    """
    Công thức tính confidence cho từng nhóm: confidence_group_X = min(observations_X / 2, 1.0)
    Sửa đổi: Cho phép tích lũy confidence nhanh hơn để sẵn sàng dừng ở câu thứ 6-8.
    """
    group_confs = []
    for g in ["R", "I", "A", "S", "E", "C"]:
        obs = groups_asked.get(g, 0)
        # Giảm mẫu số xuống 2 để confidence tăng nhanh hơn, phục vụ tối đa 10 câu
        c = min(obs / 2.0, 1.0)
        group_confs.append(c)
    
    inv_sum = sum(1.0 / max(c, 0.01) for c in group_confs)
    harmonic_mean = len(group_confs) / inv_sum
    return round(harmonic_mean, 3)


def should_stop(confidence: float, scores: dict, question_no: int) -> bool:
    """
    HỆ THỐNG GIỚI HẠN MỚI CỦA GROQ AI:
    - Giới hạn cứng tối đa: 10 câu.
    - Lý tưởng: Dừng từ câu thứ 6 đến câu thứ 8 nếu hiệu số điểm giữa top 2 nhóm cách biệt rõ ràng (> 12%).
    """
    # 1. Giới hạn cứng tối đa 10 câu
    if question_no >= 10:
        return True
        
    total = sum(scores.values()) or 1
    normalized = {k: v / total * 100 for k, v in scores.items()}
    sorted_scores = sorted(normalized.values(), reverse=True)
    if len(sorted_scores) < 3:
        return False
        
    gap_top2_vs_3 = sorted_scores[1] - sorted_scores[2]
    
    # 2. Lý tưởng dừng từ câu 6 - 8
    if question_no >= 6:
        # Giảm nhẹ GAP_THRESHOLD xuống 12% và độ tin cậy xuống 0.7 để nhạy bén hơn
        if gap_top2_vs_3 >= 12.0 and confidence >= 0.70:
            return True
            
    return False


def normalize_scores_to_100(raw_scores: dict) -> dict:
    """Chuẩn hóa điểm tích lũy về thang 0-100."""
    max_val = max(raw_scores.values()) if raw_scores else 1
    if max_val == 0:
        return {k: 0.0 for k in raw_scores}
    return {k: round(v / max_val * 100, 1) for k, v in raw_scores.items()}


async def update_user_scores(student_id: str, raw_scores: dict, confidence: float):
    """
    Gửi request PATCH đồng bộ điểm tích lũy thang 100 sang profile_service qua API nội bộ.
    """
    try:
        scores_100 = normalize_scores_to_100(raw_scores)

        sorted_groups = sorted(scores_100.keys(), key=lambda k: scores_100[k], reverse=True)
        top_groups = sorted_groups[:2]
        riasec_code = "".join(sorted_groups[:3])

        url = f"{settings.PROFILE_SERVICE_URL}/api/profile/internal/users/{student_id}/riasec-scores"
        payload = {
            "scores_100": scores_100,
            "confidence": confidence,
            "top_groups": top_groups,
            "riasec_code": riasec_code
        }

        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.patch(url, json=payload)
            if resp.status_code == 200:
                logger.info(f"[GROQ FLOW] Successfully synchronized user {student_id} scores via internal API")
            else:
                logger.error(f"[GROQ FLOW] Failed to synchronize scores: {resp.text}")
    except Exception as e:
        logger.error(f"[GROQ FLOW] update_user_scores error for {student_id}: {e}")


async def run_final_scoring_job(session_id: str, student_id: str):
    """
    Background job khi session completed (Dùng Groq API):
    Gọi Groq phân tích sâu toàn bộ hội thoại → Gửi kết quả cuối cùng sang profile_service.
    """
    db = SessionLocal()
    try:
        messages = conversation_message_repo.get_history_by_session_id(db, session_id)
        history_text = "\n".join([f"{m.role}: {m.content}" for m in messages])

        # Gọi Groq phân tích sâu hội thoại
        result = await generate_final_scoring(history_text)

        if result:
            url = f"{settings.PROFILE_SERVICE_URL}/api/profile/internal/users/{student_id}/riasec-final"
            payload = {
                "final_data": result
            }

            async with httpx.AsyncClient(timeout=15.0) as client:
                resp = await client.patch(url, json=payload)
                if resp.status_code == 200:
                    logger.info(f"[GROQ FLOW] Successfully synchronized final scoring for {session_id}")
                else:
                    logger.error(f"[GROQ FLOW] Failed to synchronize final scoring: {resp.text}")
        else:
            logger.info(f"[GROQ FLOW] Groq failed or skipped final scoring for {session_id}")
    except Exception as e:
        logger.error(f"[GROQ FLOW] Background job error for session {session_id}: {e}")
    finally:
        db.close()
