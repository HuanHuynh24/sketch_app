from uuid import UUID

import httpx
from fastapi import HTTPException, status

from app.core.config import settings


async def ensure_student_exists(student_id: UUID) -> dict:
    url = f"{settings.PROFILE_SERVICE_URL}/api/profile/students/{student_id}"

    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.get(url)
    except httpx.RequestError:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Cannot connect to profile service",
        )

    if response.status_code == 404:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Student not found",
        )

    if response.status_code >= 400:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Cannot verify student from profile service",
        )

    return response.json()
