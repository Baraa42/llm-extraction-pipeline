from __future__ import annotations

import os
from pathlib import Path
from typing import Any

from dotenv import load_dotenv
from openai import OpenAI


PROJECT_ROOT = Path(__file__).resolve().parents[1]
load_dotenv(PROJECT_ROOT / ".env", override=False)


class LLMConfigError(ValueError):
    def __init__(self, message: str, error_type: str) -> None:
        super().__init__(message)
        self.error_type = error_type


def get_backend() -> str:
    return os.environ.get("LLM_BACKEND", "openai").strip().lower()


def _supports_temperature(model: str) -> bool:
    return not model.startswith("gpt-5")


def _call_openai(prompt: str) -> str:
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        raise LLMConfigError("OPENAI_API_KEY not set", "missing_openai_api_key")

    model = os.environ.get("OPENAI_MODEL", "gpt-5-mini")
    client = OpenAI(api_key=api_key)
    request: dict[str, Any] = {
        "model": model,
        "input": prompt,
    }
    if _supports_temperature(model):
        request["temperature"] = 0

    response = client.responses.create(**request)
    return response.output_text


def _call_local(prompt: str) -> str:
    base_url = os.environ.get("LOCAL_LLM_BASE_URL")
    if not base_url:
        raise LLMConfigError("LOCAL_LLM_BASE_URL not set", "missing_local_base_url")

    model = os.environ.get("LOCAL_LLM_MODEL")
    if not model:
        raise LLMConfigError("LOCAL_LLM_MODEL not set", "missing_local_model")

    api_key = os.environ.get("LOCAL_LLM_API_KEY", "local")
    client = OpenAI(base_url=base_url, api_key=api_key)
    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "user", "content": prompt},
        ],
        temperature=0,
    )
    return response.choices[0].message.content


def call_llm(prompt: str) -> str:
    backend = get_backend()
    if backend == "openai":
        return _call_openai(prompt)
    if backend == "local":
        return _call_local(prompt)
    raise LLMConfigError(f"Unsupported LLM_BACKEND: {backend}", "unsupported_backend")
