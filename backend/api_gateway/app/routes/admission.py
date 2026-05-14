from fastapi import APIRouter, Request

from app.core.config import settings
from app.core.proxy import proxy_request


router = APIRouter()


@router.api_route("", methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"])
@router.api_route("/{path:path}", methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"])
async def forward_admission_request(request: Request, path: str = ""):
    return await proxy_request(
        request=request,
        service_url=settings.ADMISSION_SERVICE_URL,
        service_prefix="/api/admission",
        path=path,
        service_name="Admission Service",
    )