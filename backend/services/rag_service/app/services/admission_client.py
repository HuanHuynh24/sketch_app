import logging

import httpx

from app.core.config import settings


logger = logging.getLogger(__name__)


class AdmissionClient:
    def __init__(self):
        self.base_url = settings.ADMISSION_SERVICE_URL

    async def replace_recommendations(
        self,
        student_id: str,
        recommendations: list[dict],
    ) -> list[dict]:
        try:
            url = f"{self.base_url}/api/admission/recommendations/bulk"
            payload = {
                "student_id": student_id,
                "recommendations": recommendations,
            }
            logger.info(
                "Calling Admission Service: POST %s to replace %s recommendations",
                url,
                len(recommendations),
            )

            async with httpx.AsyncClient() as client:
                response = await client.post(url, json=payload, timeout=10.0)
                response.raise_for_status()
                return response.json()
        except Exception as exc:
            logger.error("Error saving recommendations to admission_service: %s", exc)
            return []
