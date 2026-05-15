from uuid import UUID

import httpx
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.core.config import settings


bearer_scheme = HTTPBearer()
PROFILE_REQUEST_TIMEOUT = 5.0


async def get_current_student_id(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
) -> UUID:
    student = await get_current_student(credentials)

    try:
        return UUID(str(student["student_id"]))
    except (KeyError, TypeError, ValueError):
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Invalid student data from profile service",
        )


async def get_current_student(
    credentials: HTTPAuthorizationCredentials,
) -> dict:
    url = f"{settings.PROFILE_SERVICE_URL}/api/profile/auth/me"
    headers = {
        "Authorization": f"{credentials.scheme} {credentials.credentials}",
    }

    try:
        async with httpx.AsyncClient(timeout=PROFILE_REQUEST_TIMEOUT) as client:
            response = await client.get(url, headers=headers)
    except httpx.RequestError:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Cannot connect to profile service",
        )

    if response.status_code in {
        status.HTTP_401_UNAUTHORIZED,
        status.HTTP_403_FORBIDDEN,
    }:
        raise HTTPException(
            status_code=response.status_code,
            detail=_response_detail(response),
        )

    if response.status_code >= 400:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Cannot verify current student from profile service",
        )

    return response.json()


def _response_detail(response: httpx.Response) -> str:
    try:
        data = response.json()
    except ValueError:
        return response.text or "Invalid authentication token"

    detail = data.get("detail")

    if isinstance(detail, str):
        return detail

    return "Invalid authentication token"
