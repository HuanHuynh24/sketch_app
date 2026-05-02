import os
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage
from .prompts import RIASEC_CHAT_PROMPT

def get_llm():
    """Khởi tạo model Gemini thay cho ChatGPT"""
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        return None 
        
    return ChatGoogleGenerativeAI(
        model="gemini-1.5-flash", # Dùng bản flash vì nó cực nhanh, ngang ngửa gpt-4o-mini
        temperature=0.7, 
        google_api_key=api_key
    )

def generate_next_question(chat_history_from_db: list) -> str:
    llm = get_llm()
    if not llm:
        return "[Hệ thống]: Chưa cấu hình GOOGLE_API_KEY. Vui lòng thêm vào file .env"

    messages = [SystemMessage(content=RIASEC_CHAT_PROMPT)]
    
    # Nạp lịch sử hội thoại (Logic y hệt cũ, LangChain tự lo phần dịch sang định dạng của Gemini)
    for msg in chat_history_from_db:
        if msg['role'] == 'user':
            messages.append(HumanMessage(content=msg['content']))
        else:
            messages.append(AIMessage(content=msg['content']))
            
    try:
        response = llm.invoke(messages)
        return response.content
    except Exception as e:
        return f"[Lỗi Gemini]: {str(e)}"