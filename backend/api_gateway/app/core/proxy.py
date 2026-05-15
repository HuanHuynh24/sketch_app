from collections.abc import Mapping

import httpx
from fastapi import APIRouter, HTTPException, Request, Response

from app.core.config import settings

HOP_BY_HOP_HEADERS = {
    "connection",
    "keep-alive",
    "proxy-authenticate",
    "proxy-authorization",
    "te",
    "trailer",
    "transfer-encoding",
    "upgrade",
    "content-encoding",
    "content-length",
}

PROXY_METHODS = ["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"]


def build_target_url(service_url: str, service_prefix: str, path: str = "") -> str:
    target_url = f"{service_url.rstrip('/')}/{service_prefix.strip('/')}"

    if path:
        target_url = f"{target_url}/{path}"

    return target_url


def filter_request_headers(headers: Mapping[str, str]) -> dict[str, str]:
    return {
        key: value
        for key, value in headers.items()
        if key.lower() not in {"host", "content-length"}
    }


def filter_response_headers(headers: Mapping[str, str]) -> dict[str, str]:
    return {
        key: value
        for key, value in headers.items()
        if key.lower() not in HOP_BY_HOP_HEADERS
    }


async def proxy_request(
    request: Request,
    service_url: str,
    service_prefix: str,
    path: str = "",
    service_name: str = "Service",
) -> Response:
    target_url = build_target_url(service_url, service_prefix, path)
    headers = filter_request_headers(dict(request.headers))
    body = await request.body()

    try:
        async with httpx.AsyncClient(
            timeout=settings.PROXY_TIMEOUT,
            follow_redirects=False,
        ) as client:
            response = await client.request(
                method=request.method,
                url=target_url,
                headers=headers,
                params=request.query_params,
                content=body,
            )

        return Response(
            content=response.content,
            status_code=response.status_code,
            headers=filter_response_headers(dict(response.headers)),
            media_type=response.headers.get("content-type"),
        )

    except httpx.ConnectError:
        raise HTTPException(
            status_code=503,
            detail=f"{service_name} is unavailable",
        )

    except httpx.TimeoutException:
        raise HTTPException(
            status_code=504,
            detail=f"{service_name} request timeout",
        )

    except httpx.RequestError as exc:
        raise HTTPException(
            status_code=503,
            detail=f"{service_name} proxy error: {str(exc)}",
        )


def create_proxy_router(
    service_url: str,
    service_prefix: str,
    service_name: str,
) -> APIRouter:
    router = APIRouter()

    @router.api_route("", methods=PROXY_METHODS)
    @router.api_route("/{path:path}", methods=PROXY_METHODS)
    async def forward_service_request(request: Request, path: str = ""):
        return await proxy_request(
            request=request,
            service_url=service_url,
            service_prefix=service_prefix,
            path=path,
            service_name=service_name,
        )

    return router
