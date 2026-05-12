from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.endpoints import riasec

app = FastAPI(title="RIASEC Service")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(riasec.router, prefix="/api/riasec", tags=["RIASEC"])

@app.get("/health")
def health_check():
    return {"status": "ok"}