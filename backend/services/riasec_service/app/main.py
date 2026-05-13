from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.endpoints import riasec_groq
from app.api.endpoints import riasec

#pp = FastAPI(title="RIASEC Service (Groq Super Speed)")
app = FastAPI(title="RIASEC Service (Gemini 2.5)")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Nạp Router mới từ riasec_groq thay vì riasec.py cũ
#app.include_router(riasec_groq.router, prefix="/api/riasec", tags=["RIASEC"])

app.include_router(riasec.router, prefix="/api/riasec", tags=["RIASEC"])
@app.get("/health")
def health_check():
    return {"status": "ok"}