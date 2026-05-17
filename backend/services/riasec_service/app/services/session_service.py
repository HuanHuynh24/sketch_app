from datetime import datetime
from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.core.constants import (
    MESSAGE_ROLE_ASSISTANT,
    MESSAGE_ROLE_USER,
    SESSION_STATUS_COMPLETED,
    SESSION_STATUS_IN_PROGRESS,
)
from app.repositories.message_repository import MessageRepository
from app.repositories.profile_repository import ProfileRepository
from app.repositories.score_snapshot_repository import ScoreSnapshotRepository
from app.repositories.session_repository import SessionRepository
from app.services.adaptive_engine import AdaptiveEngine
from app.services.answer_quality_service import AnswerQualityService
from app.services.conversation_style_service import ConversationStyleService
from app.services.question_generation_service import QuestionGenerationService
from app.services.question_policy import QuestionPolicy
from app.services.report_service import ReportService
from app.services.scoring_engine import ScoringEngine


class SessionService:
    def __init__(self, db: Session):
        self.session_repo = SessionRepository(db)
        self.message_repo = MessageRepository(db)
        self.snapshot_repo = ScoreSnapshotRepository(db)
        self.profile_repo = ProfileRepository(db)

        self.scoring_engine = ScoringEngine()
        self.adaptive_engine = AdaptiveEngine()
        self.report_service = ReportService()
        self.answer_quality_service = AnswerQualityService()
        self.conversation_style_service = ConversationStyleService()
        self.question_generation_service = QuestionGenerationService()
        self.question_policy = QuestionPolicy()

    def get_session_or_404(self, session_id: UUID):
        session = self.session_repo.get_by_id(session_id)

        if not session:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="RIASEC session not found",
            )

        return session

    async def start_session(self, student_id: UUID):
        session = self.session_repo.create(student_id)
        intro_messages = [
            self.message_repo.create(
                session_id=session.session_id,
                role=MESSAGE_ROLE_ASSISTANT,
                content=item["content"],
                message_type=item["message_type"],
                metadata_json=item.get("metadata_json"),
            )
            for item in self.conversation_style_service.build_opening_messages()
        ]
        question_data = await self.question_generation_service.generate_anchor_question()

        question = self.message_repo.create(
            session_id=session.session_id,
            role=MESSAGE_ROLE_ASSISTANT,
            content=question_data["content"],
            message_type=question_data.get("type", "anchor_scenario"),
            metadata_json=question_data,
        )

        return {
            "session": session,
            "question": question,
            "assistant_messages": [
                *intro_messages,
                question,
            ],
        }

    async def submit_answer(
        self,
        session_id: UUID,
        answer_text: str,
        student_id: UUID,
    ):
        session = self.get_session_or_404(session_id)
        self._ensure_session_owner(session, student_id)
        self._ensure_session_in_progress(session)

        history_before_answer = self.message_repo.list_by_session(session.session_id)
        last_question_message = self.question_policy.find_last_question_message(
            history_before_answer
        )
        last_question = last_question_message.content if last_question_message else ""

        quality_result = await self.answer_quality_service.validate(
            scenario=last_question,
            answer_text=answer_text,
        )

        if not quality_result["is_valid"]:
            return self._save_invalid_answer_warning(
                session=session,
                answer_text=answer_text,
                last_question=last_question,
                quality_result=quality_result,
            )

        user_message = self.message_repo.create(
            session_id=session.session_id,
            role=MESSAGE_ROLE_USER,
            content=answer_text,
            message_type="answer",
        )

        scoring_result = await self.scoring_engine.score_answer(
            scenario=last_question,
            answer_text=answer_text,
        )

        new_scores = scoring_result.scores.model_dump()
        new_confidence = scoring_result.confidence.model_dump()
        question_focus_groups = self._extract_question_focus_groups(
            last_question_message
        )

        scoring_signal = self._build_scoring_signal(
            last_question_message=last_question_message,
            focus_groups=question_focus_groups,
            scoring_result=scoring_result,
            scores=new_scores,
            confidence=new_confidence,
        )
        user_message = self.message_repo.update_signal(
            message=user_message,
            riasec_signal=scoring_signal,
        )

        session.scores = self.scoring_engine.merge_scores(
            current_scores=session.scores,
            new_scores=new_scores,
        )
        session.confidence = self.scoring_engine.merge_confidence(
            current_confidence=session.confidence,
            new_confidence=new_confidence,
            current_step=session.current_step,
        )
        session.current_step += 1
        session.entropy = self.adaptive_engine.calculate_entropy(session.scores)
        session.riasec_code = self.adaptive_engine.build_riasec_code(session.scores)

        should_stop, reason = self.adaptive_engine.should_terminate(
            current_step=session.current_step,
            scores=session.scores,
            confidence=session.confidence,
        )

        self.snapshot_repo.create(
            session_id=session.session_id,
            message_id=user_message.message_id,
            scores=session.scores,
            confidence=session.confidence,
            entropy=session.entropy,
            dominant_code=session.riasec_code,
            decision_reason=scoring_result.reasoning,
        )

        if should_stop:
            return await self._complete_session(
                session=session,
                user_message=user_message,
                reason=reason,
            )

        return await self._continue_session(
            session=session,
            user_message=user_message,
            scoring_result=scoring_result,
        )

    def _save_invalid_answer_warning(
        self,
        session,
        answer_text: str,
        last_question: str,
        quality_result: dict,
    ) -> dict:
        user_message = self.message_repo.create(
            session_id=session.session_id,
            role=MESSAGE_ROLE_USER,
            content=answer_text,
            message_type="invalid_answer",
            metadata_json={
                "quality_check": quality_result,
            },
        )

        lead_in_data = self.conversation_style_service.build_invalid_answer_lead_in()
        lead_in_message = self.message_repo.create(
            session_id=session.session_id,
            role=MESSAGE_ROLE_ASSISTANT,
            content=lead_in_data["content"],
            message_type=lead_in_data["message_type"],
            metadata_json=lead_in_data.get("metadata_json"),
        )

        warning_message = self.message_repo.create(
            session_id=session.session_id,
            role=MESSAGE_ROLE_ASSISTANT,
            content=quality_result["warning_message"],
            message_type="answer_warning",
            metadata_json={
                "reason": quality_result["reason"],
                "repeat_question": last_question,
            },
        )

        return {
            "status": session.status,
            "session": session,
            "user_message": user_message,
            "assistant_message": warning_message,
            "assistant_messages": [
                lead_in_message,
                warning_message,
            ],
            "dcp_id": None,
        }

    async def _complete_session(
        self,
        session,
        user_message,
        reason: str | None,
    ) -> dict:
        history = self.message_repo.list_by_session(session.session_id)
        history_payload = self.question_policy.build_history_payload(history)

        session.status = SESSION_STATUS_COMPLETED
        session.termination_reason = reason
        session.completed_at = datetime.utcnow()

        final_summary = await self.report_service.build_summary_with_llm(
            history=history_payload,
            scores=session.scores,
            confidence=session.confidence,
            riasec_code=session.riasec_code,
        )

        session.final_summary = final_summary
        session = self.session_repo.save(session)

        profile = self.profile_repo.create(
            student_id=session.student_id,
            session_id=session.session_id,
            riasec_code=session.riasec_code,
            scores=session.scores,
            confidence=session.confidence,
            career_groups=self.report_service.build_career_groups(session.riasec_code),
            digital_competencies=self.report_service.build_digital_competencies(
                session.riasec_code
            ),
            recommended_majors=self.report_service.build_recommended_majors(
                session.riasec_code
            ),
            summary=final_summary,
        )
        result_payload = self.report_service.build_result_payload(
            scores=session.scores,
            confidence=session.confidence,
            riasec_code=session.riasec_code,
        )

        lead_in_data = self.conversation_style_service.build_completion_lead_in(
            session.riasec_code
        )
        lead_in_message = self.message_repo.create(
            session_id=session.session_id,
            role=MESSAGE_ROLE_ASSISTANT,
            content=lead_in_data["content"],
            message_type=lead_in_data["message_type"],
            metadata_json=lead_in_data.get("metadata_json"),
        )

        assistant_message = self.message_repo.create(
            session_id=session.session_id,
            role=MESSAGE_ROLE_ASSISTANT,
            content=(
                f"Bài đánh giá đã hoàn tất. "
                f"Mã RIASEC của bạn là {session.riasec_code}. "
                f"{final_summary}"
            ),
            message_type="final_result",
            metadata_json={
                "dcp_id": str(profile.dcp_id),
                "riasec_code": session.riasec_code,
                "termination_reason": reason,
                **result_payload,
            },
        )

        return {
            "status": session.status,
            "session": session,
            "user_message": user_message,
            "assistant_message": assistant_message,
            "assistant_messages": [
                lead_in_message,
                assistant_message,
            ],
            "dcp_id": profile.dcp_id,
        }

    async def _continue_session(
        self,
        session,
        user_message,
        scoring_result,
    ) -> dict:
        history = self.message_repo.list_by_session(session.session_id)
        asked_focus_groups = self.question_policy.extract_asked_focus_groups(history)

        focus_groups = self.adaptive_engine.find_focus_groups(
            scores=session.scores,
            confidence=session.confidence,
            asked_focus_groups=asked_focus_groups,
        )

        session.current_focus_groups = focus_groups
        session = self.session_repo.save(session)

        question_data = await self.question_generation_service.generate_adaptive_question(
            history=history,
            scores=session.scores,
            confidence=session.confidence,
            focus_groups=focus_groups,
            question_number=session.current_step + 1,
        )

        transition_data = self.conversation_style_service.build_transition_message(
            scoring_result=scoring_result,
            current_step=session.current_step,
            max_steps=session.max_steps,
        )
        transition_message = self.message_repo.create(
            session_id=session.session_id,
            role=MESSAGE_ROLE_ASSISTANT,
            content=transition_data["content"],
            message_type=transition_data["message_type"],
            metadata_json=transition_data.get("metadata_json"),
        )

        assistant_message = self.message_repo.create(
            session_id=session.session_id,
            role=MESSAGE_ROLE_ASSISTANT,
            content=question_data["content"],
            message_type=question_data.get("type", "adaptive_scenario"),
            metadata_json=question_data,
        )

        return {
            "status": session.status,
            "session": session,
            "user_message": user_message,
            "assistant_message": assistant_message,
            "assistant_messages": [
                transition_message,
                assistant_message,
            ],
            "dcp_id": None,
        }

    def _ensure_session_owner(self, session, student_id: UUID) -> None:
        if session.student_id != student_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You do not have access to this RIASEC session",
            )

    def _ensure_session_in_progress(self, session) -> None:
        if session.status != SESSION_STATUS_IN_PROGRESS:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Session is not in progress",
            )

    def _extract_question_focus_groups(self, question_message) -> list[str]:
        if not question_message or not question_message.metadata_json:
            return []

        focus_groups = question_message.metadata_json.get("focus_groups") or []

        return [
            str(group)
            for group in focus_groups
        ]

    def _build_scoring_signal(
        self,
        last_question_message,
        focus_groups: list[str],
        scoring_result,
        scores: dict,
        confidence: dict,
    ) -> dict:
        return {
            "scenario_message_id": (
                str(last_question_message.message_id)
                if last_question_message
                else None
            ),
            "scenario_type": (
                last_question_message.message_type
                if last_question_message
                else None
            ),
            "focus_groups": focus_groups,
            "scores": scores,
            "confidence": confidence,
            "primary_groups": scoring_result.primary_groups,
            "detected_traits": scoring_result.detected_traits,
            "evidence": [
                item.model_dump()
                for item in scoring_result.evidence
            ],
            "reasoning": scoring_result.reasoning,
        }
