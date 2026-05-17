import httpx
import logging

from app.core.config import settings
from app.schemas.query import SearchQueryModel

logger = logging.getLogger(__name__)

class AdmissionClient:
    def __init__(self):
        self.base_url = settings.ADMISSION_SERVICE_URL
        
    async def search_programs(self, query: SearchQueryModel) -> list[dict]:
        """
        Gọi sang admission_service để query PostgreSQL bằng các field có cấu trúc.
        """
        try:
            payload = {
                "countries": query.target_countries,
                "majors": query.target_majors,
                "max_tuition": query.budget_limit_usd,
                "min_ielts": query.min_ielts
            }
            
            url = f"{self.base_url}/api/admission/programs/search"
            logger.info(f"Calling Admission Service: POST {url} with {payload}")
            
            async with httpx.AsyncClient() as client:
                response = await client.post(url, json=payload, timeout=10.0)
                response.raise_for_status()
                return response.json()
            
        except Exception as exc:
            logger.error(f"Error calling admission_service: {exc}")
            return []

    async def save_programs(self, programs_data: list[dict]) -> list[dict]:
        """
        Lưu danh sách trường học vào PostgreSQL thông qua admission_service.
        """
        try:
            url = f"{self.base_url}/api/admission/programs/bulk"
            logger.info(f"Calling Admission Service: POST {url} to save {len(programs_data)} programs")
            
            async with httpx.AsyncClient() as client:
                response = await client.post(url, json=programs_data, timeout=10.0)
                response.raise_for_status()
                return response.json()
        except Exception as exc:
            logger.error(f"Error saving programs to admission_service: {exc}")
            return []
