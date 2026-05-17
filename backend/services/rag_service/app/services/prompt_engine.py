class PromptEngine:
    def build_query_generation_prompt(
        self,
        student_profile: dict,
        riasec_result: dict,
    ) -> str:
        return f"""
You are an admissions recommendation query builder.

Student profile:
{student_profile}

RIASEC result:
{riasec_result}

Task:
Build one concise semantic-search query for the internal university knowledge
base stored in PostgreSQL pgvector. Also extract the metadata needed for
filtering and display.

Rules:
1. If the target country or province is Vietnam, write the query in Vietnamese.
   Otherwise, write it in English.
2. Focus on majors, admission methods, exam subjects, degree level, target
   location, IELTS/TOEIC, budget, scholarships, tuition, and career fit.
3. Prefer terms that are likely to appear in university admission documents.
4. Remove filler words and personal pronouns.

Return only valid JSON:
{{
  "optimized_query": "...",
  "target_countries": ["..."],
  "target_majors": ["..."],
  "budget_limit_usd": 15000,
  "min_ielts": 6.5,
  "keywords": ["..."]
}}
"""
