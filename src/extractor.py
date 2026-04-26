from __future__ import annotations

import json
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from dotenv import load_dotenv
from openai import OpenAI
from pydantic import ValidationError

from src.prompt import build_extraction_prompt, build_repair_prompt
from src.schemas import ExtractionRecord


PROJECT_ROOT = Path(__file__).resolve().parents[1]
load_dotenv(PROJECT_ROOT / ".env", override=False)


@dataclass
class ExtractionResult:
    record: ExtractionRecord | None
    raw_response: str | None
    final_raw_response: str | None
    error: str | None
    error_type: str | None
    attempts: int
    repaired: bool


class EmptyResponseError(ValueError):
    pass


def parse_model_json(raw_text: str) -> dict[str, Any]:
    """Extract and parse the first valid JSON object from model output."""
    text = raw_text.strip()

    decoder = json.JSONDecoder()
    for index, char in enumerate(text):
        if char != "{":
            continue

        try:
            parsed, _ = decoder.raw_decode(text[index:])
        except json.JSONDecodeError:
            continue

        if isinstance(parsed, dict):
            return parsed

    raise json.JSONDecodeError("No valid JSON object found", text, 0)


def _supports_temperature(model: str) -> bool:
    return not model.startswith("gpt-5")


def classify_extraction_error(exc: Exception) -> str:
    if isinstance(exc, json.JSONDecodeError):
        return "json_parse_error"
    if isinstance(exc, ValidationError):
        return "schema_validation_error"
    if isinstance(exc, EmptyResponseError):
        return "empty_response"
    if isinstance(exc, ValueError) and str(exc) == "OPENAI_API_KEY not set":
        return "missing_api_key"
    if exc.__class__.__module__.startswith("openai"):
        return "api_error"
    return "unknown_error"


def _error_string(exc: Exception) -> str:
    return f"{type(exc).__name__}: {exc}"


def _call_model(client: OpenAI, model: str, prompt: str) -> str:
    request: dict[str, Any] = {
        "model": model,
        "input": prompt,
    }
    if _supports_temperature(model):
        request["temperature"] = 0

    response = client.responses.create(**request)
    raw_response = response.output_text
    if not raw_response:
        raise EmptyResponseError("Model returned empty response")
    return raw_response


def _parse_and_validate(raw_response: str) -> ExtractionRecord:
    parsed_json = parse_model_json(raw_response)
    return ExtractionRecord(**parsed_json)


def extract_record_result(input_text: str, max_attempts: int = 2) -> ExtractionResult:
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        exc = ValueError("OPENAI_API_KEY not set")
        return ExtractionResult(
            record=None,
            raw_response=None,
            final_raw_response=None,
            error=_error_string(exc),
            error_type=classify_extraction_error(exc),
            attempts=0,
            repaired=False,
        )

    model = os.environ.get("OPENAI_MODEL", "gpt-5-mini")
    client = OpenAI(api_key=api_key)

    raw_response: str | None = None
    final_raw_response: str | None = None

    try:
        raw_response = _call_model(client, model, build_extraction_prompt(input_text))
        final_raw_response = raw_response
        record = _parse_and_validate(raw_response)
        return ExtractionResult(
            record=record,
            raw_response=raw_response,
            final_raw_response=final_raw_response,
            error=None,
            error_type=None,
            attempts=1,
            repaired=False,
        )
    except Exception as first_exc:
        first_error_type = classify_extraction_error(first_exc)
        if first_error_type not in {"json_parse_error", "schema_validation_error"} or max_attempts < 2:
            return ExtractionResult(
                record=None,
                raw_response=raw_response,
                final_raw_response=final_raw_response,
                error=_error_string(first_exc),
                error_type=first_error_type,
                attempts=1,
                repaired=False,
            )

        try:
            repair_prompt = build_repair_prompt(input_text, raw_response or "", _error_string(first_exc))
            final_raw_response = _call_model(client, model, repair_prompt)
            record = _parse_and_validate(final_raw_response)
            return ExtractionResult(
                record=record,
                raw_response=raw_response,
                final_raw_response=final_raw_response,
                error=None,
                error_type=None,
                attempts=2,
                repaired=True,
            )
        except Exception as repair_exc:
            return ExtractionResult(
                record=None,
                raw_response=raw_response,
                final_raw_response=final_raw_response,
                error=_error_string(repair_exc),
                error_type=classify_extraction_error(repair_exc),
                attempts=2,
                repaired=False,
            )


def extract_record(input_text: str) -> ExtractionRecord:
    result = extract_record_result(input_text)
    if result.record is None:
        raise ValueError(result.error or "Extraction failed")
    return result.record
