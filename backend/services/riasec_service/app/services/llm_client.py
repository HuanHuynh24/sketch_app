import asyncio
import json
import logging
import re
from typing import Type

from google import genai
from google.genai import types
from pydantic import BaseModel, ValidationError

from app.core.config import settings


logger = logging.getLogger(__name__)


class LLMClient:
    def __init__(self):
        self.model = settings.GEMINI_MODEL
        self.client = None

        if settings.GEMINI_API_KEY:
            self.client = genai.Client(api_key=settings.GEMINI_API_KEY)

    async def generate_json(
        self,
        prompt: str,
        schema: Type[BaseModel] | None = None,
        temperature: float = 0.5,
        retries: int = 2,
    ) -> dict:
        if not self.client:
            raise RuntimeError("GEMINI_API_KEY is not configured")

        last_error = None

        schema_name = schema.__name__ if schema else "dict"

        for attempt in range(retries + 1):
            try:
                return await asyncio.to_thread(
                    self._generate_json_sync,
                    prompt,
                    schema,
                    temperature,
                )
            except Exception as exc:
                last_error = exc
                logger.warning(
                    "Gemini JSON generation attempt %s/%s failed for schema=%s model=%s: %s",
                    attempt + 1,
                    retries + 1,
                    schema_name,
                    self.model,
                    exc,
                )

        logger.error(
            "Gemini JSON generation failed after retries for schema=%s model=%s",
            schema_name,
            self.model,
            exc_info=(
                (type(last_error), last_error, last_error.__traceback__)
                if last_error
                else None
            ),
        )
        raise RuntimeError(f"Gemini JSON generation failed: {last_error}") from last_error

    def _generate_json_sync(
        self,
        prompt: str,
        schema: Type[BaseModel] | None,
        temperature: float,
    ) -> dict:
        config_kwargs = {
            "temperature": temperature,
            "top_p": 0.9,
            "response_mime_type": "application/json",
        }

        if schema:
            config_kwargs["response_schema"] = schema

        response = self.client.models.generate_content(
            model=self.model,
            contents=prompt,
            config=types.GenerateContentConfig(**config_kwargs),
        )

        if schema:
            parsed = getattr(response, "parsed", None)

            if parsed is not None:
                try:
                    if isinstance(parsed, BaseModel):
                        return parsed.model_dump()

                    return schema.model_validate(parsed).model_dump()
                except ValidationError as exc:
                    raise ValueError(f"Invalid Gemini parsed schema: {exc}") from exc

        raw_text = response.text or ""
        data = self._parse_json(raw_text)

        if schema:
            try:
                return schema.model_validate(data).model_dump()
            except ValidationError as exc:
                preview = raw_text[:1000]
                raise ValueError(
                    f"Invalid Gemini JSON schema: {exc}. Raw response preview: {preview}"
                ) from exc

        return data

    def _parse_json(self, text: str) -> dict:
        text = text.strip()

        try:
            return json.loads(text)
        except json.JSONDecodeError:
            pass

        code_block = re.search(r"```json\s*(.*?)\s*```", text, re.DOTALL)

        if code_block:
            return json.loads(code_block.group(1).strip())

        json_object = re.search(r"\{.*\}", text, re.DOTALL)

        if json_object:
            return json.loads(json_object.group(0).strip())

        raise ValueError(f"Cannot parse Gemini JSON response: {text}")
