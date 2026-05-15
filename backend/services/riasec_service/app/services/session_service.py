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
from app.schemas.llm import AnswerQualityResult, GeneratedQuestion
from app.services.adaptive_engine import AdaptiveEngine
from app.services.llm_client import LLMClient
from app.services.prompt_engine import PromptEngine
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
        self.prompt_engine = PromptEngine()
        self.report_service = ReportService()
        self.llm_client = LLMClient()

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

        prompt = self.prompt_engine.build_anchor_prompt()

        try:
            question_data = await self.llm_client.generate_json(
                prompt=prompt,
                schema=GeneratedQuestion,
                temperature=0.75,
            )
        except Exception:
            question_data = {
                "type": "anchor_scenario",
                "content": (
                    "Trường bạn tổ chức một dự án xây dựng không gian học tập thông minh. "
                    "Dự án cần nhiều vai trò: chuẩn bị thiết bị, phân tích dữ liệu học sinh, "
                    "thiết kế ý tưởng, hỗ trợ các bạn sử dụng, thuyết trình kêu gọi tài trợ "
                    "và lập kế hoạch triển khai. Nếu được chọn một vai trò chính, bạn muốn làm gì nhất? Vì sao?"
                ),
                "focus_groups": ["R", "I", "A", "S", "E", "C"],
                "context": "anchor",
                "question_style": "role_choice",
            }

        question_data = self._normalize_question_data(
            question_data=question_data,
            default_type="anchor_scenario",
            focus_groups=["R", "I", "A", "S", "E", "C"],
            fallback_context="anchor",
            fallback_style="role_choice",
        )

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
        }

    async def submit_answer(
        self,
        session_id: UUID,
        answer_text: str,
        student_id: UUID,
    ):
        session = self.get_session_or_404(session_id)
        self._ensure_session_owner(session, student_id)

        if session.status != SESSION_STATUS_IN_PROGRESS:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Session is not in progress",
            )

        history_before_answer = self.message_repo.list_by_session(session.session_id)
        last_question = self._find_last_assistant_question(history_before_answer)

        quality_result = await self._validate_answer_quality(
            scenario=last_question,
            answer_text=answer_text,
        )

        if not quality_result["is_valid"]:
            user_message = self.message_repo.create(
                session_id=session.session_id,
                role=MESSAGE_ROLE_USER,
                content=answer_text,
                message_type="invalid_answer",
                metadata_json={
                    "quality_check": quality_result,
                },
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
                "dcp_id": None,
            }

        user_message = self.message_repo.create(
            session_id=session.session_id,
            role=MESSAGE_ROLE_USER,
            content=answer_text,
            message_type="answer",
        )

        history = self.message_repo.list_by_session(session.session_id)

        scoring_result = await self.scoring_engine.score_answer(
            scenario=last_question,
            answer_text=answer_text,
        )

        new_scores = scoring_result.scores.model_dump()
        new_confidence = scoring_result.confidence.model_dump()

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

        assistant_message = None
        dcp_id = None

        if should_stop:
            history_payload = self._build_history_payload(history)

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
                digital_competencies=self.report_service.build_digital_competencies(session.riasec_code),
                recommended_majors=self.report_service.build_recommended_majors(session.riasec_code),
                summary=final_summary,
            )

            dcp_id = profile.dcp_id

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
                    "dcp_id": str(dcp_id),
                    "riasec_code": session.riasec_code,
                    "termination_reason": reason,
                },
            )

        else:
            asked_focus_groups = self._extract_asked_focus_groups(history)

            focus_groups = self.adaptive_engine.find_focus_groups(
                scores=session.scores,
                confidence=session.confidence,
                asked_focus_groups=asked_focus_groups,
            )

            session.current_focus_groups = focus_groups
            session = self.session_repo.save(session)

            history_payload = self._build_history_payload(history)
            suggested_context = self._select_next_context(history)
            banned_topics = self._extract_banned_topics(history)
            question_style = self._select_next_question_style(history)

            prompt = self.prompt_engine.build_adaptive_prompt(
                history=history_payload,
                scores=session.scores,
                confidence=session.confidence,
                focus_groups=focus_groups,
                suggested_context=suggested_context,
                banned_topics=banned_topics,
                question_number=session.current_step + 1,
                question_style=question_style,
            )

            try:
                question_data = await self.llm_client.generate_json(
                    prompt=prompt,
                    schema=GeneratedQuestion,
                    temperature=0.9,
                )

                question_data = self._normalize_question_data(
                    question_data=question_data,
                    default_type="adaptive_scenario",
                    focus_groups=focus_groups,
                    fallback_context=suggested_context,
                    fallback_style=question_style,
                )

                question_data = self._ensure_question_not_repeated(
                    question_data=question_data,
                    history=history,
                    focus_groups=focus_groups,
                )

            except Exception:
                question_data = self._fallback_adaptive_question(
                    focus_groups=focus_groups,
                    history=history,
                    context=suggested_context,
                    question_style=question_style,
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
            "dcp_id": dcp_id,
        }

    def _ensure_session_owner(self, session, student_id: UUID) -> None:
        if session.student_id != student_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You do not have access to this RIASEC session",
            )

    async def _validate_answer_quality(
        self,
        scenario: str,
        answer_text: str,
    ) -> dict:
        text = answer_text.strip()

        local_invalid_phrases = {
            "ok",
            "oke",
            "ừ",
            "ừm",
            "không biết",
            "ko biết",
            "k biết",
            "sao cũng được",
            "tùy",
            "abc",
            "test",
            "haha",
            "hehe",
            "...",
        }

        if len(text) < 8:
            return {
                "is_valid": False,
                "reason": "Câu trả lời quá ngắn để đánh giá.",
                "warning_message": (
                    "Câu trả lời của bạn quá ngắn nên hệ thống chưa thể đánh giá. "
                    "Hãy nói rõ bạn sẽ chọn hướng nào và vì sao."
                ),
            }

        if text.lower() in local_invalid_phrases:
            return {
                "is_valid": False,
                "reason": "Câu trả lời không nghiêm túc hoặc không đủ thông tin.",
                "warning_message": (
                    "Câu trả lời của bạn chưa đủ rõ hoặc chưa đúng trọng tâm. "
                    "Hãy trả lời nghiêm túc hơn bằng cách nói bạn sẽ chọn hướng nào và vì sao."
                ),
            }

        prompt = self.prompt_engine.build_answer_quality_prompt(
            scenario=scenario,
            answer_text=answer_text,
        )

        try:
            data = await self.llm_client.generate_json(
                prompt=prompt,
                schema=AnswerQualityResult,
                temperature=0.1,
            )

            result = AnswerQualityResult.model_validate(data)

            if result.is_valid:
                return {
                    "is_valid": True,
                    "reason": result.reason,
                    "warning_message": None,
                }

            return {
                "is_valid": False,
                "reason": result.reason,
                "warning_message": result.warning_message
                or (
                    "Câu trả lời của bạn chưa đủ rõ hoặc chưa đúng trọng tâm. "
                    "Hãy nói rõ bạn sẽ chọn hướng nào và vì sao."
                ),
            }

        except Exception:
            return {
                "is_valid": True,
                "reason": "Quality check fallback passed.",
                "warning_message": None,
            }

    def _find_last_assistant_question(self, history) -> str:
        for message in reversed(history):
            if message.role == MESSAGE_ROLE_ASSISTANT:
                return message.content

        return ""

    def _build_history_payload(self, history) -> list[dict]:
        return [
            {
                "role": message.role,
                "type": message.message_type,
                "content": message.content,
            }
            for message in history[-10:]
        ]

    def _extract_asked_focus_groups(self, history) -> list[list[str]]:
        asked_focus_groups = []

        for message in history:
            if message.role == MESSAGE_ROLE_ASSISTANT and message.metadata_json:
                focus = message.metadata_json.get("focus_groups")

                if focus:
                    asked_focus_groups.append(sorted(focus))

        return asked_focus_groups

    def _normalize_question_data(
        self,
        question_data: dict,
        default_type: str,
        focus_groups: list[str],
        fallback_context: str | None = None,
        fallback_style: str | None = None,
    ) -> dict:
        content = str(question_data.get("content", "")).strip()

        if not content:
            content = (
                "Bạn đang tham gia một hoạt động ở trường và cần chọn một vai trò cụ thể. "
                "Bạn muốn làm phần nào nhất, bạn sẽ làm gì và vì sao?"
            )

        return {
            "type": question_data.get("type") or default_type,
            "content": content,
            "focus_groups": question_data.get("focus_groups") or focus_groups,
            "context": question_data.get("context") or fallback_context,
            "question_style": question_data.get("question_style") or fallback_style,
        }

    def _select_next_context(self, history) -> str:
        contexts = [
            "hoạt động CLB học thuật",
            "ngày hội hướng nghiệp của trường",
            "cuộc thi sáng tạo trẻ",
            "dự án thiết kế sản phẩm học tập",
            "chiến dịch truyền thông cho trường",
            "khảo sát nhu cầu chọn ngành của học sinh",
            "buổi tư vấn chọn ngành cho học sinh lớp 12",
            "xây dựng một ứng dụng nhỏ cho lớp",
            "làm video hoặc poster giới thiệu ngành nghề",
            "tổ chức sự kiện cộng đồng",
            "quản lý kế hoạch cho một nhóm học sinh",
            "thiết kế tài liệu hướng dẫn cho học sinh mới",
            "xây dựng gian hàng trải nghiệm trong ngày hội trường",
            "dự án hỗ trợ bạn bè học tập",
            "một buổi thuyết trình ý tưởng trước giáo viên",
            "một nhóm nghiên cứu nhỏ trong lớp",
            "một sản phẩm truyền thông trên mạng xã hội của trường",
            "một hoạt động gây quỹ cho CLB",
            "một dự án cải thiện thư viện hoặc phòng học",
            "một workshop kỹ năng cho học sinh",
        ]

        history_text = " ".join(
            [
                message.content.lower()
                for message in history
                if message.role == MESSAGE_ROLE_ASSISTANT
            ]
        )

        for context in contexts:
            if context.lower() not in history_text:
                return context

        index = len(history) % len(contexts)
        return contexts[index]

    def _select_next_question_style(self, history) -> str:
        styles = [
            "role_choice",
            "trade_off",
            "priority_ranking",
            "conflict_scenario",
            "resource_constraint",
            "reflection",
            "next_action",
        ]

        used_styles = []

        for message in history:
            if message.role == MESSAGE_ROLE_ASSISTANT and message.metadata_json:
                style = message.metadata_json.get("question_style")
                if style:
                    used_styles.append(style)

        for style in styles:
            if style not in used_styles:
                return style

        return styles[len(used_styles) % len(styles)]

    def _extract_banned_topics(self, history) -> list[str]:
        history_text = " ".join(
            [
                message.content.lower()
                for message in history
                if message.role == MESSAGE_ROLE_ASSISTANT
            ]
        )

        topic_keywords = [
            "lỗi hệ thống",
            "phân tích log",
            "hệ thống cảm biến",
            "cảm biến",
            "thiết bị hoạt động sai",
            "không gian học tập thông minh",
            "dự án xây dựng không gian học tập",
            "trong một hoạt động mới ở trường",
        ]

        return [
            keyword
            for keyword in topic_keywords
            if keyword in history_text
        ]

    def _ensure_question_not_repeated(
        self,
        question_data: dict,
        history,
        focus_groups: list[str],
    ) -> dict:
        new_content = question_data.get("content", "").strip()
        new_lower = new_content.lower()

        previous_questions = [
            message.content.strip().lower()
            for message in history
            if message.role == MESSAGE_ROLE_ASSISTANT
        ]

        if not new_content:
            return self._fallback_adaptive_question(
                focus_groups=focus_groups,
                history=history,
                context=question_data.get("context"),
                question_style=question_data.get("question_style"),
            )

        banned_topics = self._extract_banned_topics(history)

        for topic in banned_topics:
            if topic in new_lower:
                return self._fallback_adaptive_question(
                    focus_groups=focus_groups,
                    history=history,
                    context=question_data.get("context"),
                    question_style=question_data.get("question_style"),
                )

        for old_content in previous_questions:
            if new_lower == old_content:
                return self._fallback_adaptive_question(
                    focus_groups=focus_groups,
                    history=history,
                    context=question_data.get("context"),
                    question_style=question_data.get("question_style"),
                )

            if len(new_lower) > 100 and new_lower[:100] in old_content:
                return self._fallback_adaptive_question(
                    focus_groups=focus_groups,
                    history=history,
                    context=question_data.get("context"),
                    question_style=question_data.get("question_style"),
                )

            similarity = self._simple_text_similarity(new_lower, old_content)

            if similarity >= 0.75:
                return self._fallback_adaptive_question(
                    focus_groups=focus_groups,
                    history=history,
                    context=question_data.get("context"),
                    question_style=question_data.get("question_style"),
                )

        question_data["focus_groups"] = question_data.get("focus_groups") or focus_groups
        question_data["type"] = question_data.get("type") or "adaptive_scenario"

        return question_data

    def _simple_text_similarity(self, a: str, b: str) -> float:
        a_words = set(a.split())
        b_words = set(b.split())

        if not a_words or not b_words:
            return 0.0

        intersection = len(a_words.intersection(b_words))
        union = len(a_words.union(b_words))

        return intersection / union

    def _fallback_adaptive_question(
        self,
        focus_groups: list[str],
        history,
        context: str | None = None,
        question_style: str | None = None,
    ) -> dict:
        pair = tuple(sorted(focus_groups[:2]))

        history_text = " ".join(
            [
                message.content.lower()
                for message in history
                if message.role == MESSAGE_ROLE_ASSISTANT
            ]
        )

        fallback_map = {
            ("R", "I"): [
                "Trong một cuộc thi sáng tạo, nhóm bạn cần tạo một sản phẩm mẫu. Bạn muốn tự tay thử nghiệm, lắp ráp bản mẫu hay nghiên cứu dữ liệu và nguyên lý để chọn giải pháp tốt nhất? Vì sao?",
                "CLB khoa học cần kiểm tra một mô hình mới. Bạn muốn trực tiếp thao tác với mô hình hay phân tích tài liệu, số liệu để hiểu cách nó hoạt động trước? Vì sao?",
                "Nhóm bạn làm một thiết bị hỗ trợ học tập. Bạn muốn thử nghiệm thiết bị ngoài thực tế hay phân tích số liệu phản hồi để cải tiến? Vì sao?",
            ],
            ("I", "A"): [
                "Bạn được giao cải thiện một ứng dụng học tập. Bạn muốn phân tích dữ liệu người dùng để tìm insight hay nghĩ ra ý tưởng giao diện và nội dung mới sáng tạo hơn? Vì sao?",
                "Khi làm bài thuyết trình về chọn ngành, bạn muốn đào sâu số liệu, bằng chứng hay tìm cách kể chuyện, thiết kế slide thật thu hút? Vì sao?",
                "Một dự án truyền thông cần nội dung mới. Bạn muốn nghiên cứu hành vi người xem hay tạo concept sáng tạo để gây chú ý? Vì sao?",
            ],
            ("S", "E"): [
                "Trong một dự án nhóm, có thành viên làm chậm tiến độ. Bạn muốn hỗ trợ bạn đó hiểu việc và vượt qua khó khăn hay đứng ra phân công, thúc đẩy nhóm đạt mục tiêu? Vì sao?",
                "Nếu tổ chức sự kiện cho học sinh, bạn muốn chăm sóc trải nghiệm người tham gia hay điều phối nhóm, kêu gọi hỗ trợ và thúc đẩy kết quả? Vì sao?",
                "Khi nhóm mất động lực, bạn muốn lắng nghe từng người để hỗ trợ hay đứng ra truyền cảm hứng và kéo cả nhóm hành động? Vì sao?",
            ],
            ("E", "C"): [
                "Bạn được giao phụ trách một sự kiện hướng nghiệp. Bạn muốn tập trung thuyết phục người tham gia, tạo động lực cho nhóm hay lập kế hoạch, deadline và kiểm soát tiến độ? Vì sao?",
                "Khi triển khai một dự án ở trường, bạn muốn làm người kêu gọi, dẫn dắt mọi người hay quản lý chi phí, lịch trình và danh sách công việc? Vì sao?",
                "Một CLB cần mở rộng thành viên. Bạn muốn đứng ra thuyết phục các bạn tham gia hay xây quy trình đăng ký, phân nhóm và theo dõi hoạt động? Vì sao?",
            ],
        }

        generic_candidates = [
            "Trong ngày hội hướng nghiệp của trường, bạn được giao chọn một vai trò chính. Bạn muốn chuẩn bị hoạt động thực tế, phân tích thông tin, thiết kế nội dung, hỗ trợ người tham gia, điều phối nhóm hay lập kế hoạch chi tiết? Vì sao?",
            "CLB của bạn chuẩn bị một dự án mới nhưng chỉ còn ít thời gian. Bạn sẽ ưu tiên thử nghiệm sản phẩm, nghiên cứu thông tin, sáng tạo ý tưởng, hướng dẫn các bạn, thuyết trình kêu gọi tham gia hay quản lý tiến độ? Vì sao?",
            "Lớp bạn tổ chức một hoạt động cộng đồng và đang có bất đồng trong nhóm. Bạn muốn xử lý bằng cách làm mẫu thực tế, phân tích nhu cầu, thiết kế truyền thông, hỗ trợ các bạn, đứng ra dẫn dắt hay sắp xếp lại quy trình? Vì sao?",
            "Bạn tham gia xây dựng một sản phẩm học tập cho học sinh. Nếu chỉ được chọn một bước đầu tiên, bạn sẽ thử nghiệm, phân tích dữ liệu, thiết kế trải nghiệm, hỗ trợ người dùng, giới thiệu sản phẩm hay quản lý tài liệu và kế hoạch? Vì sao?",
            "Trong một cuộc thi ý tưởng trẻ, nhóm bạn thiếu người ở nhiều phần. Bạn sẽ nhận phần làm mô hình thử nghiệm, nghiên cứu tính khả thi, xây dựng concept sáng tạo, hỗ trợ thành viên, trình bày thuyết phục hay kiểm soát kế hoạch? Vì sao?",
            "Trường muốn cải thiện trải nghiệm học tập cho học sinh. Bạn sẽ bắt đầu bằng khảo sát thực tế, phân tích kết quả, tạo ý tưởng truyền thông, trò chuyện hỗ trợ các bạn, kêu gọi mọi người tham gia hay lập quy trình triển khai? Vì sao?",
            "Một CLB cần mở rộng thành viên nhưng nguồn lực hạn chế. Bạn muốn tạo hoạt động trải nghiệm, phân tích nhóm học sinh phù hợp, thiết kế nội dung truyền thông, tư vấn trực tiếp, thuyết phục người tham gia hay quản lý danh sách đăng ký? Vì sao?",
            "Bạn được giao chuẩn bị một workshop kỹ năng cho học sinh. Bạn muốn chuẩn bị dụng cụ thực hành, nghiên cứu nội dung, thiết kế slide, hỗ trợ người tham gia, đứng ra dẫn dắt buổi học hay lập timeline chi tiết? Vì sao?",
            "Một nhóm nghiên cứu nhỏ trong lớp cần chọn hướng làm việc. Bạn muốn thử nghiệm trực tiếp, tìm hiểu tài liệu, trình bày ý tưởng sáng tạo, hỗ trợ các bạn hiểu vấn đề, đại diện nhóm trình bày hay chuẩn hóa ghi chú và tiến độ? Vì sao?",
            "Nếu phải nhìn lại một hoạt động gần đây ở trường, vai trò nào khiến bạn thấy mình phát huy tốt nhất: làm thực tế, phân tích, sáng tạo, hỗ trợ, dẫn dắt hay tổ chức công việc? Hãy kể cụ thể bạn sẽ làm gì.",
        ]

        candidates = fallback_map.get(pair, []) + generic_candidates

        for candidate in candidates:
            if candidate.lower() not in history_text:
                return {
                    "type": "adaptive_scenario",
                    "content": candidate,
                    "focus_groups": focus_groups,
                    "context": context,
                    "question_style": question_style,
                }

        question_count = len(
            [
                message
                for message in history
                if message.role == MESSAGE_ROLE_ASSISTANT
            ]
        )

        return {
            "type": "adaptive_scenario",
            "content": (
                f"Ở lượt hỏi số {question_count + 1}, hãy chọn một trải nghiệm thực tế gần đây ở trường. "
                "Bạn đã muốn đóng vai trò gì trong hoạt động đó, bạn làm gì cụ thể và vì sao vai trò đó phù hợp với bạn?"
            ),
            "focus_groups": focus_groups,
            "context": context,
            "question_style": question_style,
        }
