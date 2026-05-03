from fastapi import APIRouter
import os

router = APIRouter()

@router.get("/health")
def check_health():
    # Tự động lấy tên thư mục gốc để biết service nào đang chạy
    service_name = os.path.basename(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../..")))
    return {"status": "ok", "service": service_name}