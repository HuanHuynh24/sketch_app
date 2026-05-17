import logging
from typing import List

from fastapi import BackgroundTasks

from sqlalchemy.orm import Session
from app.schemas.query import SearchQueryModel
from app.services.query_builder import QueryBuilderService
from app.services.admission_client import AdmissionClient
from app.services.vector_search_service import VectorSearchService
from app.services.tavily_client import TavilyIngestionService

logger = logging.getLogger(__name__)


class SearchEngine:
    def __init__(self, db: Session):
        self.db = db
        self.query_builder = QueryBuilderService()
        self.admission_client = AdmissionClient()
        self.vector_search = VectorSearchService(db)
        self.tavily_service = TavilyIngestionService(db)

    async def search_universities(
        self,
        student_profile: dict,
        riasec_result: dict,
        background_tasks: BackgroundTasks,
    ) -> dict:
        """
        Thực hiện tìm kiếm 3 lớp (Structured DB -> Vector DB -> Tavily).
        Trả về kết quả có sẵn ngay lập tức, nếu thiếu dữ liệu sẽ kích hoạt Background Task.
        """
        # 1. Tạo Query và Extract Metadata
        search_query: SearchQueryModel = await self.query_builder.build_search_query(
            student_profile=student_profile,
            riasec_result=riasec_result,
        )

        original_countries = search_query.target_countries.copy()
        
        # LỚP 1: TÌM KIẾM CÓ CẤU TRÚC (PostgreSQL - admission_service)
        logger.info("Executing Layer 1: Structured Search in PostgreSQL for Domestic and Foreign")
        
        # --- Tìm trong nước (Vietnam) ---
        search_query.target_countries = ["Vietnam", "Việt Nam"]
        domestic_db = await self.admission_client.search_programs(search_query)
        
        # --- Tìm nước ngoài ---
        foreign_targets = [c for c in original_countries if c.lower() not in ["vietnam", "việt nam", "vn"]]
        search_query.target_countries = foreign_targets # Nếu rỗng thì nó sẽ tìm toàn cầu
        foreign_db = await self.admission_client.search_programs(search_query)
        # Lọc bỏ VN khỏi danh sách nước ngoài (nếu target_countries rỗng, admission_service sẽ trả cả VN)
        foreign_db = [p for p in foreign_db if p.get("country", "").lower() not in ["vietnam", "việt nam", "vn"]]

        domestic_results = domestic_db[:10]
        foreign_results = foreign_db[:10]

        # Khôi phục lại query ban đầu
        search_query.target_countries = original_countries

        # LỚP 2: TÌM KIẾM NGỮ NGHĨA (Vector DB - rag_service)
        # Bổ sung kết quả từ ChromaDB nếu còn thiếu
        if len(domestic_results) < 10 or len(foreign_results) < 10:
            logger.info("Executing Layer 2: Semantic Search in Vector DB to fill gaps")
            vector_results = await self.vector_search.search_similar_programs(
                query=search_query.optimized_query,
                limit=15
            )
            import uuid
            for p in vector_results:
                vector_id = f"vector_{uuid.uuid4().hex[:8]}"
                p["id"] = vector_id
                meta = p.get("metadata", {})
                p["university_name"] = meta.get("university_name", "Unknown (From Vector Search)")
                p["source_url"] = meta.get("source_url", "")
                
                # Cố gắng suy đoán đây là trường trong nước hay nước ngoài dựa vào metadata hoặc query
                # Vì ChromaDB không có filter cứng, ta tạm đưa vào foreign nếu thiếu, hoặc domestic nếu query có chữ VN
                is_vn_query = "vietnam" in search_query.optimized_query.lower() or "việt nam" in search_query.optimized_query.lower()
                if is_vn_query and len(domestic_results) < 10:
                    domestic_results.append(p)
                elif not is_vn_query and len(foreign_results) < 10:
                    foreign_results.append(p)

        # LỚP 3: CẬP NHẬT DỮ LIỆU TỪ INTERNET (Tavily Search & Extract)
        is_crawling = False
        if len(domestic_results) < 5 or len(foreign_results) < 5:
            logger.info("Not enough structured results. Triggering Layer 3: Tavily Ingestion (Background)")
            is_crawling = True
            background_tasks.add_task(
                self.tavily_service.ingest_data_background,
                search_query=search_query
            )
            
        final_data = {
            "domestic": domestic_results,
            "foreign": foreign_results
        }
            
        return {
            "query_used": search_query.model_dump(),
            "results_count": len(domestic_results) + len(foreign_results),
            "is_background_crawling": is_crawling,
            "data": final_data
        }
