# Local Inference

## Overview

The extractor can use either the OpenAI API backend or a local OpenAI-compatible backend. Local backends are useful for later model comparisons against servers such as llama.cpp, Ollama, LM Studio, or vLLM.

The local model must expose an OpenAI-compatible endpoint. The local backend currently uses OpenAI-compatible Chat Completions (`/v1/chat/completions`) for broad compatibility with local runtimes. The pipeline still uses the same parsing, schema validation, reliability metadata, and repair retry behavior.

## Backend selection

Use `LLM_BACKEND`:

```bash
LLM_BACKEND=openai
```

or:

```bash
LLM_BACKEND=local
```

If `LLM_BACKEND` is not set, it defaults to `openai`.

## Environment variables

OpenAI backend:

```bash
LLM_BACKEND=openai
OPENAI_API_KEY=your_api_key_here
OPENAI_MODEL=gpt-5-mini
```

Local backend:

```bash
LLM_BACKEND=local
LOCAL_LLM_BASE_URL=http://localhost:8080/v1
LOCAL_LLM_API_KEY=local
LOCAL_LLM_MODEL=qwen-model-name
```

`LOCAL_LLM_API_KEY` defaults to `local` because many local servers require an API key field but ignore it. `LOCAL_LLM_BASE_URL` and `LOCAL_LLM_MODEL` are required in local mode.

## llama.cpp-compatible server

Common default base URL:

```bash
LOCAL_LLM_BASE_URL=http://localhost:8080/v1
```

Set `LOCAL_LLM_MODEL` to the model name exposed by your server. Verify the exact endpoint and model name for your runtime.

## Ollama-compatible endpoint

Common OpenAI-compatible base URL:

```bash
LOCAL_LLM_BASE_URL=http://localhost:11434/v1
```

Ollama exposes OpenAI-compatible Chat Completions at `/v1/chat/completions` under this base URL. Set `LOCAL_LLM_MODEL` to an installed model and verify your Ollama configuration.

## LM Studio-compatible endpoint

Common base URL:

```bash
LOCAL_LLM_BASE_URL=http://localhost:1234/v1
```

LM Studio commonly exposes OpenAI-compatible Chat Completions at `/v1/chat/completions`. Set `LOCAL_LLM_MODEL` to the model name shown by LM Studio and verify your runtime.

## Docker host networking

When the app runs directly on the host, local model URLs can use:

```bash
LOCAL_LLM_BASE_URL=http://localhost:8080/v1
```

When the app runs inside Docker and the local model server is running on the Mac host, `localhost` inside the container refers to the container itself. For Docker Desktop on Mac/Windows, use:

```bash
LOCAL_LLM_BASE_URL=http://host.docker.internal:8080/v1
```

Example Docker run:

```bash
docker run --rm -p 8000:8000 \
  -e LLM_BACKEND=local \
  -e LOCAL_LLM_BASE_URL=http://host.docker.internal:8080/v1 \
  -e LOCAL_LLM_API_KEY=local \
  -e LOCAL_LLM_MODEL=qwen-model-name \
  llm-extraction-pipeline
```

## Running a smoke test

```bash
LLM_BACKEND=local \
LOCAL_LLM_BASE_URL=http://localhost:8080/v1 \
LOCAL_LLM_API_KEY=local \
LOCAL_LLM_MODEL=qwen-model-name \
poetry run python scripts/run_extract.py \
  --text "Hi, Sarah from Acme needs help migrating Zendesk by May 15. Budget is $12k."
```

## Running a dataset sample

```bash
LLM_BACKEND=local \
LOCAL_LLM_BASE_URL=http://localhost:8080/v1 \
LOCAL_LLM_API_KEY=local \
LOCAL_LLM_MODEL=qwen-model-name \
poetry run python scripts/run_extract.py \
  --gold data/gold/gold_v2.jsonl \
  --out data/predictions/gold_v2_local_sample.jsonl \
  --limit 5
```

## Caveats

- local model quality may be worse than `gpt-5-mini`
- local model JSON reliability may vary
- schema failures can use the existing repair path
- benchmark comparisons should be run on `gold_v2.jsonl`
- local server latency and context limits depend on the runtime and model
