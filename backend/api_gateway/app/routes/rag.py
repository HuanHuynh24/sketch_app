from app.core.config import settings
from app.core.proxy import create_proxy_router


router = create_proxy_router(
    service_url=settings.RAG_SERVICE_URL,
    service_prefix="/api/rag",
    service_name="RAG Service",
)
