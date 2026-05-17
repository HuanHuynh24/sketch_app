import asyncio
import logging
from tavily import AsyncTavilyClient

from sqlalchemy.orm import Session
from app.core.config import settings
from app.schemas.query import SearchQueryModel
from app.schemas.program_extract import ExtractionResult
from app.services.llm_client import LLMClient
from app.services.admission_client import AdmissionClient
from app.services.vector_search_service import VectorSearchService

logger = logging.getLogger(__name__)

class TavilyIngestionService:
    def __init__(self, db: Session):
        self.db = db
        self.llm_client = LLMClient()
        self.admission_client = AdmissionClient()
        self.vector_search = VectorSearchService(db)
        self.tavily_client = None
        if settings.TAVILY_API_KEY:
            self.tavily_client = AsyncTavilyClient(api_key=settings.TAVILY_API_KEY)
        
    async def ingest_data_background(self, search_query: SearchQueryModel):
        """
        Background task: Chạy ngầm để không block request của user.
        """
        if not self.tavily_client:
            logger.warning("[BACKGROUND TASK] TAVILY_API_KEY không được cấu hình. Bỏ qua crawl data.")
            return

        logger.info(f"[BACKGROUND TASK] Bắt đầu cào dữ liệu cho query: {search_query.optimized_query}")
        
        try:
            # 1. Gọi Tavily Search API để lấy danh sách URL
            search_response = await self.tavily_client.search(
                query=search_query.optimized_query,
                search_depth="advanced",
                max_results=5,
                include_raw_content=False
            )
            
            urls = [result["url"] for result in search_response.get("results", [])]
            logger.info(f"[BACKGROUND TASK] Tìm thấy {len(urls)} URLs. Đang lọc...")
            
            # 2. Lọc URL (bỏ wikipedia, các trang rác)
            valid_urls = self._filter_urls(urls)
            logger.info(f"[BACKGROUND TASK] Còn lại {len(valid_urls)} URLs hợp lệ.")
            
            if not valid_urls:
                return

            # 3. Gọi Tavily Extract API lấy raw text (tối đa 3 urls mỗi lần để tiết kiệm credit/thời gian)
            extract_response = await self.tavily_client.extract(urls=valid_urls[:3])
            raw_contents = [r.get("raw_content", "") for r in extract_response.get("results", [])]
            
            # 4. Đưa raw text qua LLM (Gemini) để Schema Mapping thành JSON chuẩn
            all_extracted_programs = []
            for i, content in enumerate(raw_contents):
                if not content:
                    continue
                # Giới hạn text để khỏi tốn quá nhiều token
                snippet = content[:15000] 
                prompt = f"Trích xuất các thông tin chương trình Đại học từ văn bản sau:\n\n{snippet}\n\nYêu cầu convert học phí ra USD."
                
                try:
                    data = await self.llm_client.generate_json(
                        prompt=prompt,
                        schema=ExtractionResult,
                        temperature=0.1
                    )
                    parsed_result = ExtractionResult.model_validate(data)
                    
                    # Gắn source url vào mỗi program
                    for p in parsed_result.programs:
                        p_dict = p.model_dump()
                        p_dict["source_url"] = valid_urls[i]
                        all_extracted_programs.append(p_dict)
                except Exception as llm_exc:
                    logger.error(f"[BACKGROUND TASK] Lỗi khi trích xuất LLM: {llm_exc}")
            
            logger.info(f"[BACKGROUND TASK] LLM đã trích xuất được {len(all_extracted_programs)} chương trình.")
            
            if not all_extracted_programs:
                return

            # 5. Gọi admission_service để lưu JSON chuẩn vào PostgreSQL
            saved_programs = await self.admission_client.save_programs(all_extracted_programs)
            logger.info(f"[BACKGROUND TASK] Đã lưu {len(saved_programs)} chương trình vào Database PostgreSQL.")
            
            # 6. Gọi vector_search_service để chunking và lưu vào pgvector
            for idx, content in enumerate(raw_contents):
                if content:
                    meta = {
                        "source_url": valid_urls[idx],
                        "query": search_query.optimized_query
                    }
                    await self.vector_search.save_chunk(content[:5000], meta) # Giới hạn size của 1 chunk
            
            logger.info("[BACKGROUND TASK] Hoàn tất quá trình Data Ingestion & Schema Mapping. Dữ liệu đã sẵn sàng cho user tiếp theo!")
            
        except Exception as exc:
            logger.error(f"[BACKGROUND TASK] Lỗi trong quá trình ingest dữ liệu: {exc}")

    def _filter_urls(self, urls: list[str]) -> list[str]:
        banned_domains = ["wikipedia.org", "reddit.com", "quora.com", "facebook.com"]
        valid = []
        for u in urls:
            if not any(b in u for b in banned_domains):
                valid.append(u)
        return valid
