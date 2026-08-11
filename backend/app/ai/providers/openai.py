from typing import Any

import httpx
import structlog

from app.ai.providers.base import LLMProvider
from app.config import settings
from app.core.errors import AppError

logger = structlog.get_logger()


class OpenAILLMProvider(LLMProvider):
    def __init__(self) -> None:
        if not settings.OPENAI_API_KEY:
            raise ValueError("OPENAI_API_KEY must be set when using openai provider")
        self.api_key = settings.OPENAI_API_KEY
        self.base_url = settings.OPENAI_BASE_URL
        self.model = settings.LLM_MODEL
        self.timeout = settings.LLM_TIMEOUT_SECONDS

    async def _call_api(
        self,
        messages: list[dict[str, str]],
        temperature: float,
        seed: int | None = None,
        response_format: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        headers = {"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"}
        payload: dict[str, Any] = {
            "model": self.model,
            "messages": messages,
            "temperature": temperature,
        }
        if seed is not None:
            payload["seed"] = seed
        if response_format:
            payload["response_format"] = response_format

        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                resp = await client.post(
                    f"{self.base_url}/chat/completions", headers=headers, json=payload
                )
                resp.raise_for_status()
                return dict(resp.json())
        except httpx.HTTPStatusError as e:
            logger.error(
                "LLM Provider HTTP error", status_code=e.response.status_code, body=e.response.text
            )
            raise AppError(
                status_code=502, title="Bad Gateway", detail="Upstream LLM provider error"
            )
        except httpx.RequestError as e:
            logger.error("LLM Provider connection error", error=str(e))
            raise AppError(
                status_code=503, title="Service Unavailable", detail="LLM provider unavailable"
            )

    async def generate(
        self,
        prompt: str,
        system: str | None = None,
        temperature: float = 0.0,
        seed: int | None = None,
    ) -> str:
        messages = []
        if system:
            messages.append({"role": "system", "content": system})
        messages.append({"role": "user", "content": prompt})

        data = await self._call_api(messages, temperature, seed)
        return str(data["choices"][0]["message"]["content"])

    async def generate_json(
        self,
        prompt: str,
        system: str | None = None,
        temperature: float = 0.0,
        seed: int | None = None,
    ) -> dict[str, Any]:
        messages = []
        if system:
            messages.append({"role": "system", "content": system})
        messages.append({"role": "user", "content": prompt})

        data = await self._call_api(
            messages, temperature, seed, response_format={"type": "json_object"}
        )
        content = data["choices"][0]["message"]["content"]
        import json

        try:
            return dict(json.loads(content))
        except json.JSONDecodeError:
            logger.error("LLM did not return valid JSON", content=content)
            raise AppError(
                status_code=500, title="LLM Error", detail="Failed to parse structured output"
            )
