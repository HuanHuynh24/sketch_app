import logging
import re
import unicodedata

from fastapi import BackgroundTasks
from sqlalchemy.orm import Session

from app.schemas.query import SearchQueryModel
from app.services.admission_client import AdmissionClient
from app.services.document_ingestion_service import DocumentIngestionService
from app.services.document_rendering_service import DocumentRenderingService
from app.services.query_builder import QueryBuilderService
from app.services.vector_search_service import VectorSearchService


logger = logging.getLogger(__name__)

RECOMMENDATIONS_PER_TYPE = 5
VECTOR_OVERSAMPLE_LIMIT = 40


class SearchEngine:
    def __init__(self, db: Session):
        self.query_builder = QueryBuilderService()
        self.admission_client = AdmissionClient()
        self.vector_search = VectorSearchService(db)
        self.ingestion_service = DocumentIngestionService(db)
        self.document_renderer = DocumentRenderingService()

    async def search_universities(
        self,
        student_profile: dict,
        riasec_result: dict,
        background_tasks: BackgroundTasks,
    ) -> dict:
        search_query = await self.query_builder.build_search_query(
            student_profile=student_profile,
            riasec_result=riasec_result,
        )

        await self.ingestion_service.ingest_if_empty()

        vector_query = self._build_vector_query(
            search_query,
            student_profile,
            riasec_result,
        )
        domestic_results = await self._search_recommendation_group(
            query=vector_query,
            country_scope="domestic",
        )
        foreign_results = await self._search_recommendation_group(
            query=vector_query,
            country_scope="foreign",
        )

        final_data = {
            "domestic": domestic_results,
            "foreign": foreign_results,
        }

        saved_recommendations = await self._save_university_recommendations(
            student_profile=student_profile,
            riasec_result=riasec_result,
            domestic_results=final_data["domestic"],
            foreign_results=final_data["foreign"],
        )

        return {
            "query_used": search_query.model_dump(),
            "results_count": len(final_data["domestic"]) + len(final_data["foreign"]),
            "is_background_crawling": False,
            "saved_recommendations_count": len(saved_recommendations),
            "recommendations": saved_recommendations,
            "data": final_data,
        }

    async def _search_recommendation_group(
        self,
        query: str,
        country_scope: str,
    ) -> list[dict]:
        results = await self.vector_search.search_similar_programs(
            query=query,
            limit=VECTOR_OVERSAMPLE_LIMIT,
            country_scope=country_scope,
        )
        return self._unique_recommendation_results(results)[:RECOMMENDATIONS_PER_TYPE]

    def _unique_recommendation_results(self, results: list[dict]) -> list[dict]:
        unique_results = []
        seen = set()

        for result in results:
            metadata = result.get("metadata") or {}
            university_name = self._first_text(
                result.get("university_name"),
                metadata.get("university_name"),
            ).lower()
            major_name = self._first_text(
                result.get("major_name"),
                metadata.get("major_name"),
                metadata.get("matched_major"),
                "general program",
            ).lower()

            key = (university_name, major_name)
            if not university_name or key in seen:
                continue

            seen.add(key)
            unique_results.append(result)

        return unique_results

    def _build_vector_query(
        self,
        search_query: SearchQueryModel,
        student_profile: dict,
        riasec_result: dict,
    ) -> str:
        parts = [
            search_query.optimized_query,
            "Majors: " + ", ".join(search_query.target_majors),
            "Keywords: " + ", ".join(search_query.keywords),
            "RIASEC: " + str(riasec_result.get("riasec_code") or ""),
            "Career groups: " + ", ".join(riasec_result.get("career_groups") or []),
            "Recommended majors: " + ", ".join(self._recommended_majors(riasec_result)),
            "Target country: " + str(student_profile.get("target_country") or ""),
            "Target province: " + str(student_profile.get("target_province") or ""),
        ]
        return "\n".join(part for part in parts if part.strip())

    def _is_domestic_result(self, result: dict) -> bool:
        metadata = result.get("metadata") or {}
        country = self._first_text(result.get("country"), metadata.get("country")).lower()
        return country in {"vietnam", "viet nam", "việt nam", "vn"}

    async def _save_university_recommendations(
        self,
        student_profile: dict,
        riasec_result: dict,
        domestic_results: list[dict],
        foreign_results: list[dict],
    ) -> list[dict]:
        student_id = student_profile.get("student_id")

        if not student_id:
            logger.warning("Cannot save recommendations because student_id is missing")
            return []

        recommendations = []
        seen = set()

        for item in domestic_results:
            recommendation = self._build_recommendation_payload(
                student_id=student_id,
                program=item,
                recommendation_type=0,
                student_profile=student_profile,
                riasec_result=riasec_result,
            )
            self._append_unique_recommendation(recommendations, seen, recommendation)

        for item in foreign_results:
            recommendation = self._build_recommendation_payload(
                student_id=student_id,
                program=item,
                recommendation_type=1,
                student_profile=student_profile,
                riasec_result=riasec_result,
            )
            self._append_unique_recommendation(recommendations, seen, recommendation)

        if not recommendations:
            logger.info("No university recommendations to save")
            return []

        return await self.admission_client.replace_recommendations(
            student_id=str(student_id),
            recommendations=recommendations,
        )

    def _append_unique_recommendation(
        self,
        recommendations: list[dict],
        seen: set[tuple[str, str, int]],
        recommendation: dict,
    ) -> None:
        key = (
            recommendation["name_universities"].lower(),
            recommendation["name_majors"].lower(),
            recommendation["type"],
        )
        if key in seen:
            return

        seen.add(key)
        recommendations.append(recommendation)

    def _build_recommendation_payload(
        self,
        student_id: str,
        program: dict,
        recommendation_type: int,
        student_profile: dict,
        riasec_result: dict,
    ) -> dict:
        metadata = program.get("metadata")
        if not isinstance(metadata, dict):
            metadata = {}

        university_name = self._first_text(
            program.get("university_name"),
            program.get("name_universities"),
            metadata.get("university_name"),
            "Unknown University",
        )
        major_name = self._first_text(
            program.get("major_name"),
            program.get("name_majors"),
            metadata.get("major_name"),
            metadata.get("matched_major"),
            self._first_recommended_major(riasec_result),
        )

        logo = (
            program.get("logo")
            or program.get("logos")
            or metadata.get("logo")
            or metadata.get("images")
            or []
        )
        if isinstance(logo, str):
            logo = [logo]
        if not isinstance(logo, list):
            logo = []

        source_path = metadata.get("source_path") or program.get("source_url")
        rendered_document = self.document_renderer.render_source_document(source_path)

        content = {
            "overview": self._build_overview(program, university_name, major_name),
            "document": rendered_document,
            "matched_context": program.get("content"),
            "career_opportunities": self._build_career_opportunities(riasec_result),
            "tuition_fee": {
                "value": program.get("tuition_fee"),
                "currency": program.get("currency"),
                "display": self._format_tuition(program),
            },
            "admission_method": {
                "ielts_requirement": program.get("ielts_requirement"),
                "gpa_requirement": program.get("gpa_requirement"),
                "deadline": program.get("deadline"),
                "student_scores": {
                    "math": student_profile.get("score_math"),
                    "literature": student_profile.get("score_literature"),
                    "optional_subject_1": student_profile.get("optional_subject_1"),
                    "score_optional_1": student_profile.get("score_optional_1"),
                    "optional_subject_2": student_profile.get("optional_subject_2"),
                    "score_optional_2": student_profile.get("score_optional_2"),
                    "ielts": student_profile.get("ielts_score"),
                    "toeic": student_profile.get("toeic_score"),
                },
            },
            "advantages": self._build_advantages(
                program=program,
                student_profile=student_profile,
                riasec_result=riasec_result,
            ),
            "riasec": {
                "code": riasec_result.get("riasec_code"),
                "recommended_majors": self._recommended_majors(riasec_result),
                "career_groups": riasec_result.get("career_groups", []),
            },
            "source": {
                "url": program.get("source_url"),
                "path": source_path,
                "country": program.get("country"),
                "city": program.get("city"),
                "degree_level": program.get("degree_level"),
                "similarity_score": program.get("score"),
            },
        }

        return {
            "student_id": str(student_id),
            "logo": logo,
            "content": content,
            "description": self._build_card_description(
                program=program,
                metadata=metadata,
                university_name=university_name,
                recommendation_type=recommendation_type,
            ),
            "type": recommendation_type,
            "name_universities": university_name[:200],
            "name_majors": major_name[:200],
        }

    def _build_card_description(
        self,
        program: dict,
        metadata: dict,
        university_name: str,
        recommendation_type: int,
    ) -> str:
        if recommendation_type == 0:
            school_type = self._first_text(
                metadata.get("school_type"),
                self._extract_labeled_value(program.get("content"), "loai truong", "school type"),
                "Đang cập nhật",
            )
            address = self._first_text(
                metadata.get("address"),
                self._extract_labeled_value(program.get("content"), "dia chi", "address"),
                "Đang cập nhật",
            )
            return f"Loại trường: {school_type}; Địa chỉ: {address}."

        country = self._first_text(
            program.get("country"),
            metadata.get("country"),
            "Đang cập nhật",
        )
        city = self._first_text(
            metadata.get("city"),
            self._extract_labeled_value(program.get("content"), "thanh pho", "city"),
            "Đang cập nhật",
        )
        school_type = self._first_text(
            metadata.get("school_type"),
            self._extract_labeled_value(program.get("content"), "loai truong", "school type", "type"),
            "Đang cập nhật",
        )
        return (
            f"Tên trường: {university_name}; Quốc gia: {country}; "
            f"Thành phố: {city}; Loại trường: {school_type}."
        )

    def _build_overview(
        self,
        program: dict,
        university_name: str,
        major_name: str,
    ) -> str:
        metadata = program.get("metadata") or {}
        region = metadata.get("region") or program.get("city") or "Vietnam"
        return (
            f"{university_name} is matched for {major_name} from the local university "
            f"knowledge base in {region}. The match uses Gemini embeddings over the "
            "stored admission documents and the student's RIASEC/profile signals."
        )

    def _build_career_opportunities(self, riasec_result: dict) -> list[str]:
        recommendations = riasec_result.get("career_recommendations") or {}
        roles = recommendations.get("suitable_roles") or []

        if roles:
            return roles[:6]

        return riasec_result.get("career_groups", [])[:6]

    def _build_advantages(
        self,
        program: dict,
        student_profile: dict,
        riasec_result: dict,
    ) -> list[str]:
        advantages = []

        major_name = self._first_text(
            program.get("major_name"),
            program.get("name_majors"),
            "",
        )
        if major_name and major_name in self._recommended_majors(riasec_result):
            advantages.append("Major matches the student's RIASEC recommendations.")

        target_country = student_profile.get("target_country")
        target_province = student_profile.get("target_province")
        country = program.get("country")
        city = program.get("city")

        if target_country and country and target_country.lower() in country.lower():
            advantages.append("Country matches the student's target country.")
        elif target_province and city and target_province.lower() in city.lower():
            advantages.append("Location matches the student's target province or city.")

        ielts_score = self._to_float(student_profile.get("ielts_score"))
        ielts_requirement = self._to_float(program.get("ielts_requirement"))
        if (
            ielts_score is not None
            and ielts_requirement is not None
            and ielts_score >= ielts_requirement
        ):
            advantages.append("IELTS score meets the listed requirement.")

        if program.get("score") is not None:
            advantages.append("Strong semantic match in the university knowledge base.")

        if not advantages:
            advantages.append("Recommendation is based on matched major and available admission data.")

        return advantages

    def _format_tuition(self, program: dict) -> str | None:
        tuition = program.get("tuition_fee")
        if tuition is None:
            return None

        currency = program.get("currency") or "USD"
        return f"{tuition} {currency}"

    def _recommended_majors(self, riasec_result: dict) -> list[str]:
        return (
            riasec_result.get("recommended_majors")
            or riasec_result.get("career_recommendations", {}).get("recommended_majors")
            or []
        )

    def _first_recommended_major(self, riasec_result: dict) -> str:
        majors = self._recommended_majors(riasec_result)
        return majors[0] if majors else "General Program"

    def _first_text(self, *values) -> str:
        for value in values:
            if value is None:
                continue

            text = str(value).strip()
            if text:
                return text

        return ""

    def _extract_labeled_value(self, text: str | None, *labels: str) -> str | None:
        if not text:
            return None

        normalized_labels = {self._normalize_text(label) for label in labels}
        for line in text.splitlines():
            cleaned = re.sub(r"^[\s>*-]+", "", line).strip()
            cleaned = re.sub(r"[*_`]", "", cleaned).strip()
            if ":" not in cleaned:
                continue

            raw_label, raw_value = cleaned.split(":", 1)
            if self._normalize_text(raw_label) not in normalized_labels:
                continue

            value = re.sub(r"[<>{}\[\]()*_`]", "", raw_value).strip()
            if value:
                return value

        return None

    def _normalize_text(self, value: str) -> str:
        value = value.replace("Đ", "D").replace("đ", "d")
        normalized = unicodedata.normalize("NFD", value)
        without_accents = "".join(
            char for char in normalized if unicodedata.category(char) != "Mn"
        )
        return without_accents.lower().strip()

    def _to_float(self, value) -> float | None:
        if value is None:
            return None

        try:
            return float(value)
        except (TypeError, ValueError):
            return None
