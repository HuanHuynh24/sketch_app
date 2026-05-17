import logging
import uuid
import chromadb

logger = logging.getLogger(__name__)

class VectorSearchService:
    def __init__(self, db=None):
        # Không cần db PostgreSQL nữa, Chroma tự lưu vào ổ cứng
        self.client = chromadb.PersistentClient(path="/app/chroma_data")
        # Tự động dùng model local (all-MiniLM-L6-v2) miễn phí 100%
        self.collection = self.client.get_or_create_collection(name="university_programs")

    async def search_similar_programs(self, query: str, limit: int = 5) -> list[dict]:
        """Tìm kiếm ngữ nghĩa (Semantic Search) trong ChromaDB"""
        logger.info(f"Đang thực hiện Semantic Search trong ChromaDB với limit {limit}")
        try:
            results = self.collection.query(
                query_texts=[query],
                n_results=limit
            )
            
            formatted_results = []
            if results and results["documents"] and len(results["documents"][0]) > 0:
                for i in range(len(results["documents"][0])):
                    formatted_results.append({
                        "content": results["documents"][0][i],
                        "metadata": results["metadatas"][0][i]
                    })
            return formatted_results
        except Exception as exc:
            logger.error(f"Lỗi khi search ChromaDB: {exc}")
            return []
            
    async def save_chunk(self, content: str, meta: dict):
        """Lưu trữ một chunk văn bản vào ChromaDB (AI tự sinh Vector)"""
        try:
            chunk_id = str(uuid.uuid4())
            self.collection.add(
                documents=[content],
                metadatas=[meta],
                ids=[chunk_id]
            )
            logger.info("Đã lưu thành công 1 chunk vào ChromaDB (Local Embedding).")
        except Exception as exc:
            logger.error(f"Lỗi khi lưu chunk vào ChromaDB: {exc}")
