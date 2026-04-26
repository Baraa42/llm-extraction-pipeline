from __future__ import annotations

from typing import Annotated, Any

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

from src.extractor import ExtractionResult, extract_record_result


app = FastAPI(title="LLM Extraction Pipeline")


class ExtractRequest(BaseModel):
    text: Annotated[str, Field(min_length=1)]


def extraction_result_to_response(result: ExtractionResult) -> dict[str, Any]:
    return {
        "prediction": result.record.model_dump(mode="json") if result.record else None,
        "raw_response": result.raw_response,
        "final_raw_response": result.final_raw_response,
        "error": result.error,
        "error_type": result.error_type,
        "attempts": result.attempts,
        "repaired": result.repaired,
    }


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/extract")
def extract(request: ExtractRequest) -> dict[str, Any]:
    input_text = request.text.strip()
    if not input_text:
        raise HTTPException(status_code=422, detail="text must not be empty")

    result = extract_record_result(input_text)
    return extraction_result_to_response(result)
