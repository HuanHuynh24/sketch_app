from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Import đầy đủ 4 router
from app.routes import admission, profile, riasec, rag

app = FastAPI(title="API Gateway - Sketch App")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Gắn (Include) 4 router vào API chính
app.include_router(admission.router, prefix="/api/admission", tags=["Admission"])
app.include_router(profile.router, prefix="/api/profile", tags=["Profile"])
app.include_router(riasec.router, prefix="/api/riasec", tags=["RIASEC"])
app.include_router(rag.router, prefix="/api/rag", tags=["RAG"])

@app.get("/health")
def health_check():
    return {"status": "Gateway is running perfectly!"}