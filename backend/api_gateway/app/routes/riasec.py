from app.core.config import settings
from app.core.proxy import create_proxy_router


router = create_proxy_router(
    service_url=settings.RIASEC_SERVICE_URL,
    service_prefix="/api/riasec",
    service_name="RIASEC Service",
)
