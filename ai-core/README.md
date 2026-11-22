# SHOHIN AI Core (online self-hosted engine)

This is the first backend foundation for one SHOHIN-owned online inference service. It does not call OpenAI, Gemini, or a paid model API. Text generation runs on the machine where this service is deployed using a local GGUF model and llama.cpp.

## App profiles

- `english` — English learning, translation and conversation practice.
- `tajik-chinese` — Mandarin Chinese learning for Tajik-speaking users; Chinese characters + pinyin + Tajik meaning.
- `dictionary` — word lookup and translation.
- `weather` — HAWO / SHOHIN WEATHER help only; no invented live weather.
- `generic` — fallback SHOHIN app profile.

## Run locally

1. Put a compatible instruction-tuned GGUF model in a folder named `models` at the project root. The default filename is `qwen3-0.6b-q4_k_m.gguf`; change `SHOHIN_MODEL_PATH` if you use another compatible file.
2. Build and start:

```bash
docker build -t shohin-ai-core ./ai-core
docker run --rm -p 8000:8000 -v "$PWD/models:/models:ro" --env-file ai-core/.env shohin-ai-core
```

3. Check `http://localhost:8000/health`.
4. Send a test request:

```bash
curl -X POST http://localhost:8000/v1/chat \
  -H "Content-Type: application/json" \
  -d '{"app_id":"tajik-chinese","language":"tg","messages":[{"role":"user","content":"Себ ба чинӣ чӣ мешавад?"}]}'
```

## API contract

POST `/v1/chat`

```json
{
  "app_id": "english",
  "language": "ru",
  "app_context": "",
  "messages": [
    {"role": "user", "content": "Как сказать «я хочу учить английский»?"}
  ]
}
```

The response contains `answer`, `app_id`, and usage metadata.

## Important deployment facts

- No paid AI API is used. The model runs on SHOHIN's own server.
- This does **not** make online inference free: a server with enough RAM/CPU (and ideally a GPU for many concurrent users) must stay online. A free hosting tier is generally not suitable for a reliable always-on LLM service.
- The browser/app must call this backend URL. Do not put a private server secret in HTML or JavaScript; anything shipped to users can be extracted.
- CORS is not authentication. The included in-memory per-IP limiter is only a development safeguard and resets on restart. Before public launch, add real user/app authentication, shared rate limiting (Redis or equivalent), request quotas, monitoring and abuse protection.
- Start with the small Qwen3 0.6B GGUF for a technical prototype. Its answer quality and throughput are limited. Test Tajik, Russian, English and Chinese carefully before using it with customers.
- Keep advertising code in each app's UI. The AI API does not need to serve or inject ads.
- Do not claim this service is deployed until a real host, model file and public HTTPS URL have been configured and tested.
