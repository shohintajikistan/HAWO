import os
from io import BytesIO

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field
from huggingface_hub import InferenceClient

app = FastAPI(title="SHOHIN AI Image Engine", version="0.1.0")

# The browser app is hosted on GitHub Pages. Restrict this list to your
# actual HAWO origin before making the service public.
ALLOWED_ORIGINS = os.getenv(
    "ALLOWED_ORIGINS",
    "https://shohintajikistan.github.io,http://localhost:8000"
).split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[origin.strip() for origin in ALLOWED_ORIGINS if origin.strip()],
    allow_credentials=False,
    allow_methods=["GET", "POST"],
    allow_headers=["Content-Type"],
)

class GenerateRequest(BaseModel):
    prompt: str = Field(min_length=4, max_length=1200)
    width: int = Field(default=1024, ge=512, le=1024)
    height: int = Field(default=1024, ge=512, le=1024)

@app.get("/health")
def health():
    return {"status": "ok", "service": "SHOHIN AI Image Engine"}

@app.post("/generate")
def generate(payload: GenerateRequest):
    token = os.getenv("HF_TOKEN")
    if not token:
        raise HTTPException(status_code=503, detail="Backend is missing HF_TOKEN secret.")

    try:
        client = InferenceClient(
            provider="fal-ai",
            api_key=token,
            timeout=180,
        )
        image = client.text_to_image(
            prompt=payload.prompt,
            model="black-forest-labs/FLUX.1-schnell",
            width=payload.width,
            height=payload.height,
            num_inference_steps=4,
        )
        output = BytesIO()
        image.save(output, format="PNG")
        output.seek(0)
        return StreamingResponse(
            output,
            media_type="image/png",
            headers={"Cache-Control": "no-store"}
        )
    except Exception as exc:
        # Return a concise provider error without exposing the token.
        raise HTTPException(status_code=502, detail=f"Image provider error: {str(exc)[:350]}")

