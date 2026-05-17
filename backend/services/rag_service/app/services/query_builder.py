import logging

from app.schemas.query import SearchQueryModel
from app.services.llm_client import LLMClient
from app.services.prompt_engine import PromptEngine


logger = logging.getLogger(__name__)


class QueryBuilderService:
    def __init__(self, enable_llm: bool = True):
        self.prompt_engine = PromptEngine()
        self.llm_client = LLMClient() if enable_llm else None

    async def build_search_query(
        self,
        student_profile: dict,
        riasec_result: dict,
    ) -> SearchQueryModel:
        """
        Takes raw JSON from Profile and RIASEC, and uses LLM to build 
        an optimized search query and extract structured metadata.
        """
        logger.info("Building search query from user profile and RIASEC results")

        prompt = self.prompt_engine.build_query_generation_prompt(
            student_profile=student_profile,
            riasec_result=riasec_result,
        )

        try:
            if not self.llm_client:
                raise RuntimeError("LLM client is disabled")

            data = await self.llm_client.generate_json(
                prompt=prompt,
                schema=SearchQueryModel,
                temperature=0.2, # Low temperature for more deterministic, focused query
            )

            result = SearchQueryModel.model_validate(data)
            logger.info(f"Generated query: {result.optimized_query}")
            return result

        except Exception as exc:
            logger.error(f"Failed to build search query with LLM: {exc}")
            # Fallback mechanism if LLM fails
            return self._build_fallback_query(student_profile, riasec_result)

    def _build_fallback_query(self, student_profile: dict, riasec_result: dict) -> SearchQueryModel:
        """
        Simple heuristic-based query builder if LLM fails or is disabled.
        """
        majors = (
            riasec_result.get("recommended_majors")
            or riasec_result.get("career_recommendations", {}).get("recommended_majors")
            or riasec_result.get("majors", [])
        )
        major_str = " ".join(majors[:2])
        
        target_province = student_profile.get("target_country") or student_profile.get("target_province", "")
        ielts = student_profile.get("ielts_score") or student_profile.get("ielts", "")
        
        query_parts = ["bachelor"]
        if major_str:
            query_parts.append(major_str)
        if target_province:
            query_parts.append(target_province)
        if ielts:
            query_parts.append(f"IELTS {ielts}")
            
        fallback_query = " ".join(query_parts)
        
        return SearchQueryModel(
            optimized_query=fallback_query,
            target_countries=[target_province] if target_province else [],
            target_majors=majors,
            budget_limit_usd=student_profile.get("target_budget"),
            min_ielts=float(ielts) if str(ielts).replace(".", "", 1).isdigit() else None,
            keywords=["university", "admission"]
        )
