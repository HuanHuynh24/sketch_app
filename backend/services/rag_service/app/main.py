from fastapi import FastAPI, Request
from pydantic import BaseModel

app = FastAPI(title="RAG Service API")

class ChatRequest(BaseModel):
    question: str

@app.post("/api/v1/rag/ask")
def ask_university_info(payload: ChatRequest, request: Request):
    student_id_str = request.headers.get("X-User-Id")
    if not student_id_str:
        return {"error": "Unauthorized. Please go through API Gateway."}
        
    # --- MOCK LOGIC RAG ---
    # Chỗ này sau này sẽ là code: Embed câu hỏi -> Tìm trong ChromaDB -> Đưa PDF vào Prompt -> Gọi Gemini
    mock_answer = f"Theo đề án tuyển sinh 2026, câu trả lời cho '{payload.question}' là: [Hệ thống đang chờ tích hợp ChromaDB]."
    
    return {
        "answer": mock_answer,
        "sources": ["De_an_tuyen_sinh_2026.pdf - Trang 12"]
    }