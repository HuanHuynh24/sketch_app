import hashlib
import math
import re
import unicodedata
from dataclasses import dataclass
from typing import Literal, Protocol

import httpx

from app.core.config import settings


EmbeddingTask = Literal["document", "query"]

LOCAL_EMBEDDING_MODEL = "local-hashing-v1"
DEFAULT_OPENAI_EMBEDDING_MODEL = "text-embedding-3-small"
DEFAULT_GEMINI_EMBEDDING_MODEL = "gemini-embedding-001"
DEPRECATED_GEMINI_EMBEDDING_MODELS = {
    "text-embedding-001",
    "models/text-embedding-001",
    "text-embedding-004",
    "models/text-embedding-004",
}


class EmbeddingProviderError(RuntimeError):
    pass


@dataclass(frozen=True)
class EmbeddingResult:
    provider: str
    model: str
    dimension: int
    vector: list[float]


class EmbeddingProvider(Protocol):
    provider_name: str
    model_name: str
    dimension: int

    def embed(self, text: str, task: EmbeddingTask = "document") -> EmbeddingResult:
        ...

    def embed_many(
        self,
        texts: list[str],
        task: EmbeddingTask = "document",
    ) -> list[EmbeddingResult]:
        ...


class HashingEmbeddingProvider:
    provider_name = "local"

    def __init__(
        self,
        dimension: int = settings.EMBEDDING_DIMENSION,
        model_name: str = LOCAL_EMBEDDING_MODEL,
    ):
        self.dimension = dimension
        self.model_name = model_name

    def embed(self, text: str, task: EmbeddingTask = "document") -> EmbeddingResult:
        vector = [0.0] * self.dimension
        terms = self._terms(text)

        for term in terms:
            digest = hashlib.sha256(term.encode("utf-8")).digest()
            index = int.from_bytes(digest[:4], byteorder="big") % self.dimension
            sign = 1.0 if digest[4] % 2 == 0 else -1.0
            vector[index] += sign

        return EmbeddingResult(
            provider=self.provider_name,
            model=self.model_name,
            dimension=self.dimension,
            vector=normalize_vector(vector),
        )

    def embed_many(
        self,
        texts: list[str],
        task: EmbeddingTask = "document",
    ) -> list[EmbeddingResult]:
        return [self.embed(text, task=task) for text in texts]

    def _terms(self, text: str) -> list[str]:
        tokens = tokenize(text)

        if not tokens:
            return []

        bigrams = [
            f"{left}_{right}"
            for left, right in zip(tokens, tokens[1:])
        ]
        return tokens + bigrams


class OpenAIEmbeddingProvider:
    provider_name = "openai"

    def __init__(
        self,
        api_key: str | None = settings.OPENAI_API_KEY,
        model_name: str | None = None,
        dimension: int = settings.EMBEDDING_DIMENSION,
        timeout: float = settings.EMBEDDING_TIMEOUT_SECONDS,
    ):
        self.api_key = api_key
        self.model_name = model_name or DEFAULT_OPENAI_EMBEDDING_MODEL
        self.dimension = dimension
        self.timeout = timeout

    def embed(self, text: str, task: EmbeddingTask = "document") -> EmbeddingResult:
        return self.embed_many([text], task=task)[0]

    def embed_many(
        self,
        texts: list[str],
        task: EmbeddingTask = "document",
    ) -> list[EmbeddingResult]:
        if not self.api_key:
            raise EmbeddingProviderError("OPENAI_API_KEY is required for OpenAI embeddings")

        if not texts:
            return []

        payload: dict[str, object] = {
            "model": self.model_name,
            "input": texts,
        }

        if self.model_name.startswith("text-embedding-3"):
            payload["dimensions"] = self.dimension

        try:
            response = httpx.post(
                settings.OPENAI_EMBEDDING_URL,
                headers={"Authorization": f"Bearer {self.api_key}"},
                json=payload,
                timeout=self.timeout,
            )
            response.raise_for_status()
        except httpx.HTTPStatusError as exc:
            raise EmbeddingProviderError(
                f"OpenAI embedding request failed: "
                f"status={exc.response.status_code}, model={self.model_name}"
            ) from exc

        data = response.json()
        rows = sorted(data["data"], key=lambda item: item["index"])

        return [self._result(row["embedding"]) for row in rows]

    def _result(self, vector: list[float]) -> EmbeddingResult:
        validate_dimension(vector, self.dimension, self.model_name)
        return EmbeddingResult(
            provider=self.provider_name,
            model=self.model_name,
            dimension=self.dimension,
            vector=normalize_vector(vector),
        )


class GeminiEmbeddingProvider:
    provider_name = "gemini"

    def __init__(
        self,
        api_key: str | None = settings.GEMINI_API_KEY,
        model_name: str | None = None,
        dimension: int = settings.EMBEDDING_DIMENSION,
        timeout: float = settings.EMBEDDING_TIMEOUT_SECONDS,
    ):
        self.api_key = api_key
        self.model_name = normalize_gemini_model_name(
            model_name or DEFAULT_GEMINI_EMBEDDING_MODEL
        )
        self.dimension = dimension
        self.timeout = timeout

    def embed(self, text: str, task: EmbeddingTask = "document") -> EmbeddingResult:
        return self.embed_many([text], task=task)[0]

    def embed_many(
        self,
        texts: list[str],
        task: EmbeddingTask = "document",
    ) -> list[EmbeddingResult]:
        if not self.api_key:
            raise EmbeddingProviderError("GEMINI_API_KEY is required for Gemini embeddings")

        if not texts:
            return []

        if len(texts) == 1:
            return [self._embed_one(texts[0], task)]

        model_path = to_gemini_model_path(self.model_name)
        requests = [
            self._request_payload(text, task, model_path)
            for text in texts
        ]

        try:
            response = httpx.post(
                f"{settings.GEMINI_EMBEDDING_URL}/{model_path}:batchEmbedContents",
                headers={"x-goog-api-key": self.api_key},
                json={"requests": requests},
                timeout=self.timeout,
            )
            response.raise_for_status()
        except httpx.HTTPStatusError as exc:
            raise EmbeddingProviderError(
                f"Gemini batch embedding request failed: "
                f"status={exc.response.status_code}, model={self.model_name}"
            ) from exc

        data = response.json()
        return [
            self._result(embedding["values"])
            for embedding in data["embeddings"]
        ]

    def _embed_one(self, text: str, task: EmbeddingTask) -> EmbeddingResult:
        model_path = to_gemini_model_path(self.model_name)
        payload = self._request_payload(text, task, model_path)

        try:
            response = httpx.post(
                f"{settings.GEMINI_EMBEDDING_URL}/{model_path}:embedContent",
                headers={"x-goog-api-key": self.api_key},
                json=payload,
                timeout=self.timeout,
            )
            response.raise_for_status()
        except httpx.HTTPStatusError as exc:
            raise EmbeddingProviderError(
                f"Gemini embedding request failed: "
                f"status={exc.response.status_code}, model={self.model_name}"
            ) from exc

        data = response.json()
        vector = data["embedding"]["values"]
        return self._result(vector)

    def _request_payload(
        self,
        text: str,
        task: EmbeddingTask,
        model_path: str,
    ) -> dict[str, object]:
        content_text = text

        if self.model_name == "gemini-embedding-2":
            content_text = with_gemini_embedding_2_instruction(text, task)

        payload: dict[str, object] = {
            "model": model_path,
            "content": {"parts": [{"text": content_text}]},
            "outputDimensionality": self.dimension,
        }

        if self.model_name == "gemini-embedding-001":
            payload["taskType"] = (
                "RETRIEVAL_QUERY" if task == "query" else "RETRIEVAL_DOCUMENT"
            )

        return payload

    def _result(self, vector: list[float]) -> EmbeddingResult:
        validate_dimension(vector, self.dimension, self.model_name)
        return EmbeddingResult(
            provider=self.provider_name,
            model=self.model_name,
            dimension=self.dimension,
            vector=normalize_vector(vector),
        )


def get_embedding_provider() -> EmbeddingProvider:
    provider = settings.EMBEDDING_PROVIDER.strip().casefold()
    configured_model = settings.EMBEDDING_MODEL.strip()

    if provider == "openai":
        model = (
            DEFAULT_OPENAI_EMBEDDING_MODEL
            if configured_model == LOCAL_EMBEDDING_MODEL
            else configured_model
        )
        return OpenAIEmbeddingProvider(model_name=model)

    if provider == "gemini":
        model = (
            DEFAULT_GEMINI_EMBEDDING_MODEL
            if configured_model == LOCAL_EMBEDDING_MODEL
            else configured_model
        )
        return GeminiEmbeddingProvider(model_name=model)

    if provider == "local":
        return HashingEmbeddingProvider(model_name=LOCAL_EMBEDDING_MODEL)

    raise EmbeddingProviderError(
        "EMBEDDING_PROVIDER must be one of: local, openai, gemini"
    )


def normalize_gemini_model_name(model_name: str) -> str:
    stripped = model_name.strip()
    normalized = stripped.removeprefix("models/")

    if stripped in DEPRECATED_GEMINI_EMBEDDING_MODELS or normalized in {
        value.removeprefix("models/")
        for value in DEPRECATED_GEMINI_EMBEDDING_MODELS
    }:
        return DEFAULT_GEMINI_EMBEDDING_MODEL

    return normalized


def to_gemini_model_path(model_name: str) -> str:
    return model_name if model_name.startswith("models/") else f"models/{model_name}"


def with_gemini_embedding_2_instruction(text: str, task: EmbeddingTask) -> str:
    if task == "query":
        return f"Represent this query for retrieving relevant admission documents: {text}"

    return f"Represent this admission document for retrieval: {text}"


def normalize_vector(vector: list[float]) -> list[float]:
    norm = math.sqrt(sum(float(value) * float(value) for value in vector))

    if norm == 0:
        return [0.0 for _ in vector]

    return [round(float(value) / norm, 8) for value in vector]


def validate_dimension(vector: list[float], expected: int, model_name: str) -> None:
    if len(vector) != expected:
        raise EmbeddingProviderError(
            f"Embedding model {model_name} returned {len(vector)} dimensions; "
            f"expected {expected}. Update EMBEDDING_DIMENSION and migration if needed."
        )


def normalize_for_embedding(value: str) -> str:
    value = value.replace("đ", "d").replace("Đ", "D")
    decomposed = unicodedata.normalize("NFD", value)
    without_marks = "".join(
        char
        for char in decomposed
        if unicodedata.category(char) != "Mn"
    )
    return without_marks.casefold()


def tokenize(text: str) -> list[str]:
    normalized = normalize_for_embedding(text)
    return re.findall(r"[a-z0-9]+", normalized)
