from sqlalchemy.orm import Session
from sqlalchemy import text
import asyncio
from app.services.llm_service import generate_final_scoring
from app.models.conversation_message import ConversationMessage
from app.core.database import SessionLocal
from app.core.config import settings
import json
import logging

logger = logging.getLogger(__name__)


def calc_confidence(scores: dict, groups_asked: dict, question_no: int) -> float:
    """
    Công thức tính confidence cho từng nhóm: confidence_group_X = min(observations_X / 3, 1.0)
    overall_confidence = harmonic_mean(confidence cho 6 nhóm)
    """
    group_confs = []
    for g in ["R", "I", "A", "S", "E", "C"]:
        obs = groups_asked.get(g, 0)
        c = min(obs / 3.0, 1.0)
        group_confs.append(c)
    
    # Calculate harmonic mean (thêm 0.01 để tránh chia cho 0)
    inv_sum = sum(1.0 / max(c, 0.01) for c in group_confs)
    harmonic_mean = len(group_confs) / inv_sum
    return round(harmonic_mean, 3)


def should_stop(confidence: float, scores: dict, question_no: int) -> bool:
    """
    Điều kiện dừng hội thoại RIASEC:
    - Giới hạn cứng: 25 câu
    - Lý tưởng: ~10-12 câu, confidence đủ cao và top 2 nhóm cách nhóm 3 > 15%
    """
    if question_no >= 25:
        return True
        
    total = sum(scores.values()) or 1
    normalized = {k: v / total * 100 for k, v in scores.items()}
    sorted_scores = sorted(normalized.values(), reverse=True)
    if len(sorted_scores) < 3:
        return False
        
    gap_top2_vs_3 = sorted_scores[1] - sorted_scores[2]
    
    if question_no >= 10 and gap_top2_vs_3 > 15.0 and confidence >= settings.CONFIDENCE_THRESHOLD:
        return True
        
    return False


def normalize_scores_to_100(raw_scores: dict) -> dict:
    """Chuẩn hóa điểm tích lũy về thang 0-100."""
    max_val = max(raw_scores.values()) if raw_scores else 1
    if max_val == 0:
        return {k: 0.0 for k in raw_scores}
    return {k: round(v / max_val * 100, 1) for k, v in raw_scores.items()}


def update_user_scores(student_id: str, raw_scores: dict, confidence: float):
    """
    Cập nhật điểm RIASEC vào bảng users SAU MỖI câu trả lời.
    Gọi trực tiếp (sync), dùng session riêng.
    """
    db = SessionLocal()
    try:
        scores_100 = normalize_scores_to_100(raw_scores)

        # Xác định top groups + riasec_code từ điểm hiện tại
        sorted_groups = sorted(scores_100.keys(), key=lambda k: scores_100[k], reverse=True)
        top_groups = sorted_groups[:2]
        riasec_code = "".join(sorted_groups[:3])

        pg_array = "{" + ",".join(top_groups) + "}"

        update_query = text("""
            UPDATE users 
            SET "score_R" = :sr, "score_I" = :si, "score_A" = :sa, 
                "score_S" = :ss, "score_E" = :se, "score_C" = :sc,
                riasec_code = :code,
                top_groups = :groups,
                confidence = :conf,
                updated_at = NOW()
            WHERE student_id = CAST(:student_id AS UUID)
        """)
        result = db.execute(update_query, {
            "sr": scores_100.get("R", 0.0),
            "si": scores_100.get("I", 0.0),
            "sa": scores_100.get("A", 0.0),
            "ss": scores_100.get("S", 0.0),
            "se": scores_100.get("E", 0.0),
            "sc": scores_100.get("C", 0.0),
            "code": riasec_code,
            "groups": pg_array,
            "conf": confidence,
            "student_id": student_id,
        })
        db.commit()
        rows = result.rowcount
        logger.info(f"Updated user {student_id} scores: {scores_100} (rows={rows})")
    except Exception as e:
        logger.error(f"update_user_scores error for {student_id}: {e}")
        db.rollback()
    finally:
        db.close()


def run_final_scoring_job(session_id: str, student_id: str):
    """
    Background job khi session completed:
    Gọi Gemini phân tích toàn bộ hội thoại → update reasoning + suggested_majors.
    Nếu Gemini không khả dụng, dùng điểm tích lũy đã update trước đó.
    """
    db = SessionLocal()
    try:
        messages = (
            db.query(ConversationMessage)
            .filter(ConversationMessage.session_id == session_id)
            .order_by(ConversationMessage.sequence_no)
            .all()
        )
        history_text = "\n".join([f"{m.role}: {m.content}" for m in messages])

        # Gọi Gemini cho detailed analysis
        result = asyncio.run(generate_final_scoring(history_text))

        if result:
            scores = result.get("scores", {})
            top_groups = result.get("top_groups", [])
            pg_array = "{" + ",".join(top_groups) + "}" if top_groups else "{}"

            update_query = text("""
                UPDATE users 
                SET riasec_code = :code, 
                    top_groups = :groups,
                    confidence = :conf, 
                    reasoning = :reason, 
                    description = :desc,
                    suggested_majors = :majors,
                    "score_R" = :sr, "score_I" = :si, "score_A" = :sa, 
                    "score_S" = :ss, "score_E" = :se, "score_C" = :sc,
                    updated_at = NOW()
                WHERE student_id = CAST(:student_id AS UUID)
            """)
            db.execute(update_query, {
                "code": result.get("riasec_code"),
                "groups": pg_array,
                "conf": result.get("confidence", 0.0),
                "reason": result.get("reasoning"),
                "desc": result.get("description"),
                "majors": json.dumps(result.get("suggested_majors", []), ensure_ascii=False),
                "sr": scores.get("R", 0.0),
                "si": scores.get("I", 0.0),
                "sa": scores.get("A", 0.0),
                "ss": scores.get("S", 0.0),
                "se": scores.get("E", 0.0),
                "sc": scores.get("C", 0.0),
                "student_id": student_id,
            })
            db.commit()
            logger.info(f"Final scoring completed for session {session_id}")
        else:
            logger.info(f"Gemini unavailable — using accumulated scores for {session_id}")
    except Exception as e:
        logger.error(f"Background job error for session {session_id}: {e}")
        db.rollback()
    finally:
        db.close()
