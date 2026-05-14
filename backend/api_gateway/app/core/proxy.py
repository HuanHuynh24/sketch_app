import httpx
from fastapi import Request, HTTPException, Response


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


def filter_request_headers(headers: dict) -> dict:
    return {
        key: value
        for key, value in headers.items()
        if key.lower() not in {"host", "content-length"}
    }


def filter_response_headers(headers: dict) -> dict:
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
    target_url = f"{service_url.rstrip('/')}/{service_prefix.strip('/')}"

    if path:
        target_url = f"{target_url}/{path}"

    headers = filter_request_headers(dict(request.headers))
    body = await request.body()

    try:
        async with httpx.AsyncClient(timeout=30.0, follow_redirects=False) as client:
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