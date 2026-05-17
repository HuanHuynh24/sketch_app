from dataclasses import dataclass

import httpx
from sqlalchemy.orm import Session

from app.core.config import settings
from app.services.text_cleaner import clean_text
from app.services.vector_index_service import VectorSearchResult, search_admission_chunks


MAX_CONTEXT_CHARS = 1200


@dataclass
class AdmissionChatSourceData:
    citation_id: int
    result: VectorSearchResult
    snippet: str


@dataclass
class AdmissionChatAnswer:
    question: str
    answer: str
    used_llm: bool
    model: str | None
    sources: list[AdmissionChatSourceData]


class AdmissionChatServiceError(RuntimeError):
    pass


def answer_admission_question(
    db: Session,
    question: str,
    top_k: int = 6,
    province: str | None = None,
    university_code: str | None = None,
    year: int | None = None,
    use_llm: bool = True,
) -> AdmissionChatAnswer:
    results = search_admission_chunks(
        db=db,
        query_text=question,
        top_k=top_k,
        province=province,
        university_code=university_code,
        year=year,
    )
    sources = build_chat_sources(results)

    if not sources:
        return AdmissionChatAnswer(
            question=question,
            answer=(
                "Mình chưa tìm thấy dữ liệu tuyển sinh phù hợp trong kho hiện tại. "
                "Bạn thử hỏi cụ thể hơn về tên trường, ngành, thành phố hoặc năm tuyển sinh."
            ),
            used_llm=False,
            model=None,
            sources=[],
        )

    if use_llm and settings.GEMINI_API_KEY:
        try:
            return AdmissionChatAnswer(
                question=question,
                answer=generate_gemini_answer(question, sources),
                used_llm=True,
                model=settings.GEMINI_MODEL,
                sources=sources,
            )
        except AdmissionChatServiceError:
            pass

    return AdmissionChatAnswer(
        question=question,
        answer=build_extractive_answer(question, sources),
        used_llm=False,
        model=None,
        sources=sources,
    )


def build_chat_sources(
    results: list[VectorSearchResult],
) -> list[AdmissionChatSourceData]:
    sources = []

    for index, result in enumerate(results, start=1):
        snippet = trim_context(result.chunk_text, MAX_CONTEXT_CHARS)
        sources.append(
            AdmissionChatSourceData(
                citation_id=index,
                result=result,
                snippet=snippet,
            )
        )

    return sources


def trim_context(text: str, max_chars: int) -> str:
    cleaned = clean_text(text) or ""

    if len(cleaned) <= max_chars:
        return cleaned

    return f"{cleaned[:max_chars].rstrip()}..."


def generate_gemini_answer(
    question: str,
    sources: list[AdmissionChatSourceData],
) -> str:
    model_path = settings.GEMINI_MODEL

    if not model_path.startswith("models/"):
        model_path = f"models/{model_path}"

    try:
        response = httpx.post(
            f"{settings.GEMINI_GENERATE_URL}/{model_path}:generateContent",
            headers={"x-goog-api-key": settings.GEMINI_API_KEY or ""},
            json={
                "contents": [
                    {
                        "role": "user",
                        "parts": [
                            {
                                "text": build_prompt(question, sources),
                            }
                        ],
                    }
                ],
                "generationConfig": {
                    "temperature": 0.2,
                    "topP": 0.9,
                    "maxOutputTokens": 900,
                },
            },
            timeout=settings.GEMINI_CHAT_TIMEOUT_SECONDS,
        )
        response.raise_for_status()
    except httpx.HTTPStatusError as exc:
        raise AdmissionChatServiceError(
            f"Gemini chat request failed: status={exc.response.status_code}, "
            f"model={settings.GEMINI_MODEL}"
        ) from exc
    except httpx.HTTPError as exc:
        raise AdmissionChatServiceError(
            f"Gemini chat request failed: {exc.__class__.__name__}, "
            f"model={settings.GEMINI_MODEL}"
        ) from exc

    data = response.json()
    parts = (
        data.get("candidates", [{}])[0]
        .get("content", {})
        .get("parts", [])
    )
    answer = "\n".join(
        part.get("text", "")
        for part in parts
        if part.get("text")
    ).strip()

    if not answer:
        raise AdmissionChatServiceError("Gemini chat response is empty")

    return answer


def build_prompt(question: str, sources: list[AdmissionChatSourceData]) -> str:
    context = "\n\n".join(
        format_source_for_prompt(source)
        for source in sources
    )

    return f"""
Bạn là chatbot tư vấn tuyển sinh đại học Việt Nam.
Chỉ được trả lời dựa trên CONTEXT bên dưới. Không bịa thông tin ngoài context.
Nếu context chưa đủ, nói rõ là dữ liệu hiện tại chưa đủ.
Trả lời bằng tiếng Việt, ngắn gọn, thực tế, dễ đọc.
Khi dùng thông tin từ nguồn nào, gắn citation dạng [1], [2] tương ứng.

QUESTION:
{question}

CONTEXT:
{context}
""".strip()


def format_source_for_prompt(source: AdmissionChatSourceData) -> str:
    result = source.result
    return f"""
[{source.citation_id}]
Trường: {result.university_name} ({result.university_code})
Tỉnh/thành: {result.province or "Không rõ"}
Năm: {result.year or "Không rõ"}
Loại tài liệu: {result.document_type}
Nguồn: {result.source_url}
Nội dung: {source.snippet}
""".strip()


def build_extractive_answer(
    question: str,
    sources: list[AdmissionChatSourceData],
) -> str:
    lines = [
        "Mình tìm thấy một số thông tin liên quan trong dữ liệu tuyển sinh:",
    ]

    for source in sources[:5]:
        result = source.result
        lines.append(
            f"[{source.citation_id}] {result.university_name} "
            f"({result.university_code}) - {source.snippet[:260].rstrip()}..."
        )

    lines.append(
        "Bạn có thể hỏi cụ thể hơn về ngành, trường, khu vực hoặc phương thức xét tuyển "
        "để mình lọc sát hơn."
    )
    return "\n".join(lines)
