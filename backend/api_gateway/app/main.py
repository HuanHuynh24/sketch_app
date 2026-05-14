from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.routes import admission, profile, riasec, rag


app = FastAPI(title=settings.APP_NAME)


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Dev only. Production nên đổi thành domain frontend cụ thể.
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(profile.router, prefix="/api/profile", tags=["Profile"])
app.include_router(riasec.router, prefix="/api/riasec", tags=["RIASEC"])
app.include_router(admission.router, prefix="/api/admission", tags=["Admission"])
app.include_router(rag.router, prefix="/api/rag", tags=["RAG"])


@app.get("/health")
def health_check():
    return {
        "status": "ok",
        "service": "api_gateway",
    }