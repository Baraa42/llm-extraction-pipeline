from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any

from dotenv import load_dotenv
from openai import OpenAI

from src.prompt import build_extraction_prompt
from src.schemas import ExtractionRecord


PROJECT_ROOT = Path(__file__).resolve().parents[1]
load_dotenv(PROJECT_ROOT / ".env", override=False)


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


def extract_record(input_text: str) -> ExtractionRecord:
    prompt = build_extraction_prompt(input_text)

    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        raise ValueError("OPENAI_API_KEY not set")

    model = os.environ.get("OPENAI_MODEL", "gpt-5-mini")

    client = OpenAI(api_key=api_key)
    request: dict[str, Any] = {
        "model": model,
        "input": prompt,
    }
    if _supports_temperature(model):
        request["temperature"] = 0

    response = client.responses.create(**request)

    parsed_json = parse_model_json(response.output_text)
    return ExtractionRecord(**parsed_json)
