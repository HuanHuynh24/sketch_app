import httpx
from fastapi import HTTPException

async def forward_request(method: str, url: str, headers: dict, params: dict, body: bytes):
    """Một hàm tiện ích dùng chung để forward request và tự động bắt lỗi."""
    async with httpx.AsyncClient() as client:
        try:
            response = await client.request(
                method=method,
                url=url,
                headers=headers,
                params=params,
                content=body,
                timeout=10.0 # Thêm timeout dùng chung
            )
            return response
        except httpx.ConnectError:
            raise HTTPException(status_code=503, detail="Service is down")
        except httpx.TimeoutException:
            raise HTTPException(status_code=504, detail="Service timeout")