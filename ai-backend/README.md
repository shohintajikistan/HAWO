---
title: SHOHIN AI Image Backend
emoji: 🎨
colorFrom: green
colorTo: emerald
sdk: docker
app_port: 7860
---

# SHOHIN AI Image Backend

FastAPI service for text-to-image generation through Hugging Face Inference Providers.

## Required Space Secret

Add `HF_TOKEN` in Settings → Variables and secrets. The token must have Inference Providers permission.

The default model is `black-forest-labs/FLUX.1-schnell` using provider `fal-ai`. Provider usage may consume paid credits. See [Hugging Face text-to-image documentation](https://huggingface.co/docs/inference-providers/en/tasks/text-to-image).

## API

- `GET /health`
- `POST /generate` with JSON: `{"prompt":"...", "width":1024, "height":1024}`
- Successful response: PNG image bytes.
