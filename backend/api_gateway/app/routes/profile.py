import httpx
from fastapi import APIRouter, Request, HTTPException, Response
from app.core.config import settings

router = APIRouter()

@router.api_route("/{path:path}", methods=["GET", "POST", "PUT", "DELETE", "PATCH"])
async def forward_profile_request(path: str, request: Request):
    # Đồng bộ URL với prefix của gateway
    url = f"{settings.PROFILE_SERVICE_URL}/api/profile/{path}"
    
    headers = dict(request.headers)
    headers.pop("host", None) # XÓA HEADER HOST (Bắt buộc cho Docker)
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.request(
                method=request.method,
                url=url,
                headers=headers,
                params=dict(request.query_params),
                content=await request.body()
            )
            # Trả về Response gốc
            return Response(
                content=response.content,
                status_code=response.status_code,
                headers=dict(response.headers)
            )
        except httpx.RequestError as exc:
            raise HTTPException(status_code=503, detail=f"Profile Service unavailable: {exc}")