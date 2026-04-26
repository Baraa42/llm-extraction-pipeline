# Deployment Readiness

## Overview

The project is Dockerized and exposes a FastAPI service. This document describes how to run it locally and outlines a Google Cloud Run deployment path.

This is deployment readiness documentation, not a full production hardening guide.

## Local Docker run

Build the image:

```bash
docker build -t llm-extraction-pipeline .
```

Run the API container:

```bash
docker run --rm -p 8000:8000 \
  --env-file .env \
  llm-extraction-pipeline
```

Health check:

```bash
curl http://127.0.0.1:8000/health
```

Extraction:

```bash
curl -X POST http://127.0.0.1:8000/extract \
  -H "Content-Type: application/json" \
  -d '{"text":"Hi, Sarah from Acme needs help migrating Zendesk by May 15. Budget is $12k."}'
```

## Required environment variables

```bash
OPENAI_API_KEY=your_api_key_here
OPENAI_MODEL=gpt-5-mini
```

`.env` is for local development only and should not be committed. `.env.example` documents the expected variables.

## Google Cloud Run deployment path

### Option A — Deploy from source

Cloud Run can deploy from source:

```bash
gcloud run deploy llm-extraction-pipeline \
  --source . \
  --region us-central1 \
  --set-env-vars OPENAI_MODEL=gpt-5-mini
```

This uses Cloud Build/buildpacks behind the scenes. If a Dockerfile is present, Cloud Run source deployment can use it, but build behavior should be tested. `OPENAI_API_KEY` still needs to be handled securely.

### Option B — Build image then deploy

Set placeholders:

```bash
PROJECT_ID=your-gcp-project
REGION=us-central1
REPOSITORY=llm-extraction
IMAGE=llm-extraction-pipeline
SERVICE=llm-extraction-pipeline
```

Create an Artifact Registry repository if needed:

```bash
gcloud artifacts repositories create $REPOSITORY \
  --repository-format=docker \
  --location=$REGION
```

Build and push with Cloud Build:

```bash
gcloud builds submit \
  --tag $REGION-docker.pkg.dev/$PROJECT_ID/$REPOSITORY/$IMAGE
```

Deploy to Cloud Run:

```bash
gcloud run deploy $SERVICE \
  --image $REGION-docker.pkg.dev/$PROJECT_ID/$REPOSITORY/$IMAGE \
  --region $REGION \
  --platform managed \
  --set-env-vars OPENAI_MODEL=gpt-5-mini
```

Do not put a real project ID or API key in source-controlled files.

## Secret handling

API keys should not be stored in source code, committed `.env` files, or Docker images. Use local environment variables for development and Secret Manager / Cloud Run secrets for production.

Create a Secret Manager secret:

```bash
echo -n "sk-..." | gcloud secrets create openai-api-key \
  --data-file=-
```

Grant the Cloud Run service account access if needed.

Deploy with the secret:

```bash
gcloud run deploy $SERVICE \
  --image $REGION-docker.pkg.dev/$PROJECT_ID/$REPOSITORY/$IMAGE \
  --region $REGION \
  --platform managed \
  --set-env-vars OPENAI_MODEL=gpt-5-mini \
  --set-secrets OPENAI_API_KEY=openai-api-key:latest
```

This is a template and may need IAM/service-account setup for a specific project.

## Production caveats

- no authentication yet
- no rate limiting yet
- no request persistence
- no audit log
- no async job queue
- no multi-tenant isolation
- not intended as a public unauthenticated production API yet
- OpenAI API costs should be monitored
- logging should avoid storing sensitive customer text unless explicitly intended

## Troubleshooting

### Docker daemon not running

Error:

```text
Cannot connect to the Docker daemon
```

Fix:

- open Docker Desktop
- wait until Docker is running

### Missing API key

Fix:

- check `.env`
- ensure the container is run with `--env-file .env`
- in Cloud Run, verify the secret or environment variable is configured

### Port already in use

Check the port:

```bash
lsof -i :8000
```

Or run with another host port:

```bash
docker run --rm -p 8001:8000 --env-file .env llm-extraction-pipeline
```

### Cloud Run auth / IAM issues

Check:

- project and region are correct
- Cloud Run, Cloud Build, Artifact Registry, and Secret Manager APIs are enabled
- service account has the required permissions

## Future improvements

- add authentication
- add rate limiting
- add structured logging
- add request persistence / audit trail
- add deployment script
- add Cloud Run CI/CD
- add latency and cost monitoring
