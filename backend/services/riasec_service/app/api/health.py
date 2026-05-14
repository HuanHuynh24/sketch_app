from fastapi import APIRouter

router = APIRouter()


@router.get("/health")
def health_check():
    return {
        "service": "riasec_service",
        "status": "ok",
    }
