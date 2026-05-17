from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from typing import Dict, Any, Optional
import httpx
import asyncio
from pydantic import BaseModel

from app.core.config import settings
from app.core.database import get_db
from app.services.search_engine import SearchEngine

router = APIRouter(prefix="/search", tags=["RAG Search"])

security = HTTPBearer(auto_error=False)

class OrchestratorSearchRequest(BaseModel):
    dcp_id: Optional[str] = None
    # Cho phép ghi đè (override) dữ liệu nếu Frontend muốn test mà không dùng DB
    override_profile: Optional[Dict[str, Any]] = None
    override_riasec: Optional[Dict[str, Any]] = None

@router.post("/universities")
async def search_universities_endpoint(
    payload: OrchestratorSearchRequest,
    background_tasks: BackgroundTasks,
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
    db: Session = Depends(get_db)
):
    """
    Orchestrator Endpoint: Tự động lấy JWT token từ Header, gọi sang profile_service 
    và riasec_service để gom dữ liệu lại, sau đó đẩy vào Search Engine.
    """
    authorization = f"Bearer {credentials.credentials}" if credentials else None
    
    student_profile = payload.override_profile or {}
    riasec_result = payload.override_riasec or {}

    # Nếu Frontend không truyền override data, tự động đi fetch
    if not payload.override_profile or (payload.dcp_id and not payload.override_riasec):
        if not authorization:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Missing Authorization header required for internal fetching"
            )
            
        headers = {"Authorization": authorization}
        
        async with httpx.AsyncClient(timeout=10.0) as client:
            tasks = []
            
            # Task 1: Lấy Profile (Student Info)
            tasks.append(client.get(f"{settings.PROFILE_SERVICE_URL}/api/profile/students/me", headers=headers))
            
            # Task 2: Lấy Academic Record
            tasks.append(client.get(f"{settings.PROFILE_SERVICE_URL}/api/profile/students/me/academic-record", headers=headers))
            
            # Task 3: Lấy RIASEC (nếu có dcp_id)
            if payload.dcp_id:
                tasks.append(client.get(f"{settings.RIASEC_SERVICE_URL}/api/riasec/profiles/{payload.dcp_id}", headers=headers))
                
            responses = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Xử lý kết quả trả về
            for i, res in enumerate(responses):
                if isinstance(res, Exception):
                    raise HTTPException(status_code=500, detail=f"Internal call failed: {str(res)}")
                
                if res.status_code != 200:
                    raise HTTPException(status_code=400, detail=f"Failed to fetch data from internal service. Status: {res.status_code}")
                    
            if not payload.override_profile:
                profile_data = responses[0].json()
                academic_data = responses[1].json()
                # Gộp 2 cái vào student_profile
                student_profile = {**profile_data, **academic_data}
                
            if payload.dcp_id and not payload.override_riasec:
                # Nếu có dcp_id thì task thứ 3 sẽ là RIASEC
                riasec_result = responses[2].json()
    
    # Khởi tạo RAG Engine với dữ liệu đã được gom đầy đủ
    engine = SearchEngine(db)
    
    return await engine.search_universities(
        student_profile=student_profile,
        riasec_result=riasec_result,
        background_tasks=background_tasks
    )
