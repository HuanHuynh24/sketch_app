import os
import httpx
import jwt
from fastapi import FastAPI, Request, HTTPException, Depends
from fastapi.responses import Response
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.middleware.cors import CORSMiddleware # MỚI: Import CORS

app = FastAPI(title="API Gateway")

# --- MỚI: THÊM CORS MIDDLEWARE ---
# Cho phép Next.js (Frontend) gọi API mà không bị trình duyệt chặn
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- 1. CẤU HÌNH BẢO MẬT & URL NỘI BỘ ---
SECRET_KEY = os.getenv("JWT_SECRET", "default_secret")
ALGORITHM = "HS256"
security = HTTPBearer()

# Danh sách domain của các Microservices nội bộ
PROFILE_SERVICE_URL = "http://ms_profile_service:8000"
RIASEC_SERVICE_URL = "http://ms_riasec_service:8000"       # MỚI
ADMISSION_SERVICE_URL = "http://ms_admission_service:8000" # MỚI
RAG_SERVICE_URL = "http://ms_rag_service:8000"             # MỚI


# --- 2. HÀM XÁC THỰC TOKEN ---
async def verify_jwt_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    token = credentials.credentials
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload.get("sub")
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token đã hết hạn")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Token không hợp lệ")


# --- 3. HÀM CHUYỂN TIẾP REQUEST (REVERSE PROXY) ---
async def forward_request(request: Request, target_url: str):
    path = request.url.path
    query = request.url.query
    full_url = f"{target_url}{path}?{query}" if query else f"{target_url}{path}"
    
    body = await request.body()
    headers = dict(request.headers)
    headers.pop("host", None)
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.request(
                method=request.method,
                url=full_url,
                content=body,
                headers=headers,
                timeout=30.0 # Tăng timeout lên 30s vì sau này AI xử lý có thể lâu
            )
            return Response(
                content=response.content, 
                status_code=response.status_code, 
                headers=dict(response.headers)
            )
        except httpx.RequestError as e:
            raise HTTPException(status_code=503, detail=f"Service đích không phản hồi: {str(e)}")


# --- 4. ĐỊNH TUYẾN (ROUTING) ---

@app.get("/")
def gateway_status():
    return {"status": "API Gateway is running smoothly on Ubuntu", "version": "1.1"}

# [PUBLIC] Không cần Token
@app.api_route("/api/v1/auth/{path:path}", methods=["GET", "POST", "PUT", "DELETE"])
async def route_auth_public(request: Request, path: str):
    return await forward_request(request, PROFILE_SERVICE_URL)

# [PRIVATE] Cần Token - Nhóm Hồ sơ
@app.api_route("/api/v1/students/{path:path}", methods=["GET", "POST", "PUT", "DELETE"])
async def route_students_private(request: Request, path: str, student_id: str = Depends(verify_jwt_token)):
    request.headers.mutablecopy()["X-User-Id"] = student_id 
    return await forward_request(request, PROFILE_SERVICE_URL)

# --- MỚI: ROUTING CHO 3 SERVICE CÒN LẠI ---
# [PRIVATE] Phân hệ 1: RIASEC AI
@app.api_route("/api/v1/riasec/{path:path}", methods=["GET", "POST", "PUT", "PATCH", "DELETE"])
async def route_riasec(request: Request, path: str, student_id: str = Depends(verify_jwt_token)):
    request.headers.mutablecopy()["X-User-Id"] = student_id 
    return await forward_request(request, RIASEC_SERVICE_URL)

# [PRIVATE] Phân hệ 2: Dự đoán tuyển sinh ML
@app.api_route("/api/v1/admission/{path:path}", methods=["GET", "POST", "PUT", "DELETE"])
async def route_admission(request: Request, path: str, student_id: str = Depends(verify_jwt_token)):
    request.headers.mutablecopy()["X-User-Id"] = student_id 
    return await forward_request(request, ADMISSION_SERVICE_URL)

# [PRIVATE] Phân hệ 3: RAG Hỏi đáp
@app.api_route("/api/v1/rag/{path:path}", methods=["GET", "POST", "PUT", "DELETE"])
async def route_rag(request: Request, path: str, student_id: str = Depends(verify_jwt_token)):
    request.headers.mutablecopy()["X-User-Id"] = student_id 
    return await forward_request(request, RAG_SERVICE_URL)