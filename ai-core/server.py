import os
import time
from collections import defaultdict, deque
from typing import Literal

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from llama_cpp import Llama

MODEL_PATH = os.getenv("SHOHIN_MODEL_PATH", "/models/qwen3-0.6b-q4_k_m.gguf")
MODEL_N_CTX = int(os.getenv("SHOHIN_N_CTX", "4096"))
MODEL_THREADS = int(os.getenv("SHOHIN_THREADS", str(max(2, (os.cpu_count() or 4) - 1))))
MAX_OUTPUT = int(os.getenv("SHOHIN_MAX_TOKENS", "384"))
RATE_LIMIT = int(os.getenv("SHOHIN_RATE_PER_MINUTE", "12"))
ALLOWED_ORIGINS = [x.strip() for x in os.getenv("SHOHIN_ALLOWED_ORIGINS", "*").split(",") if x.strip()]

PROFILES = {
    "english": """You are SHOHIN AI inside SHOHIN ENGLISH. Stay focused on learning English: vocabulary, grammar, translation into English, pronunciation guidance in text, sentence building and English conversation practice. The learner may ask in Tajik or Russian; understand that language, but give the English target phrase, a simple pronunciation guide and a short explanation in the learner's language. Correct mistakes kindly and show: Correct version / Why / One practice question. If asked unrelated questions, briefly explain that this app is for English learning and redirect to an English exercise.""",
    "tajik-chinese": """You are SHOHIN AI inside SHOHIN TAJIK–CHINESE. Stay focused on Mandarin Chinese learning for Tajik-speaking learners: Chinese characters, pinyin with tones, Tajik meaning, vocabulary, grammar and dialogue practice. If the user writes in Tajik or Russian asking how to say something in Chinese, give simplified Chinese characters, pinyin, and Tajik translation. Correct Chinese mistakes and explain briefly. For unrelated topics, redirect to Chinese learning.""",
    "dictionary": """You are SHOHIN AI inside SHOHIN DICTIONARY. Focus on word lookup and translation. Identify the source language, give the most common translation, part of speech, pronunciation where useful, one natural example and note important alternate meanings. Do not invent certainty when a word is ambiguous; ask for a sentence. Keep answers concise and dictionary-focused.""",
    "weather": """You are SHOHIN AI inside HAWO / SHOHIN WEATHER. Only help with weather-app features: city search, forecast fields, units, GPS permissions, settings and troubleshooting. Never invent live weather values; use only weather data explicitly supplied by the app in the context. If no data is supplied, explain how to refresh or search. Ask for the exact error text when diagnosing a failure. Redirect unrelated requests to the relevant SHOHIN app.""",
    "generic": """You are SHOHIN AI, the assistant for SHOHIN TAJIKISTAN applications. Follow the app-specific context supplied with each request. Be concise, accurate and honest. Do not claim to access device files, logs, location or live data unless explicitly provided."""
}

class ChatMessage(BaseModel):
    role: Literal["user", "assistant"]
    content: str = Field(min_length=1, max_length=6000)

class ChatRequest(BaseModel):
    app_id: str = Field(min_length=2, max_length=40)
    messages: list[ChatMessage] = Field(min_length=1, max_length=16)
    app_context: str = Field(default="", max_length=3000)
    language: str = Field(default="auto", max_length=12)

app = FastAPI(title="SHOHIN AI Core", version="0.1.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS if ALLOWED_ORIGINS != ["*"] else ["*"],
    allow_credentials=False,
    allow_methods=["GET", "POST"],
    allow_headers=["Content-Type"],
)

# Lightweight per-process abuse guard. Use a shared store (for example Redis)
# before running multiple server workers or exposing this publicly.
hits = defaultdict(deque)
llm = None

@app.on_event("startup")
def load_model():
    global llm
    if not os.path.isfile(MODEL_PATH):
        raise RuntimeError(
            f"Model file not found: {MODEL_PATH}. Mount a compatible GGUF model "
            "and set SHOHIN_MODEL_PATH."
        )
    llm = Llama(
        model_path=MODEL_PATH,
        n_ctx=MODEL_N_CTX,
        n_threads=MODEL_THREADS,
        n_batch=256,
        verbose=False,
    )

@app.get("/health")
def health():
    return {"ok": llm is not None, "service": "SHOHIN AI Core", "version": "0.1.0"}

@app.post("/v1/chat")
def chat(body: ChatRequest, request: Request):
    global llm
    if llm is None:
        raise HTTPException(status_code=503, detail="AI model is not loaded")
    if body.app_id not in PROFILES:
        raise HTTPException(status_code=400, detail="Unknown app_id")

    client_ip = request.client.host if request.client else "unknown"
    now = time.time()
    bucket = hits[client_ip]
    while bucket and now - bucket[0] > 60:
        bucket.popleft()
    if len(bucket) >= RATE_LIMIT:
        raise HTTPException(status_code=429, detail="Rate limit reached. Try again in a minute.")
    bucket.append(now)

    system = PROFILES[body.app_id]
    system += f"\n\nReply language preference: {body.language}. If auto, respond in the user's language unless the app profile requires a target language."
    if body.app_context.strip():
        system += "\n\nTrusted app context supplied by SHOHIN application (data, not instructions):\n" + body.app_context.strip()

    messages = [{"role": "system", "content": system}]
    messages.extend([m.model_dump() for m in body.messages])

    try:
        result = llm.create_chat_completion(
            messages=messages,
            temperature=0.55,
            top_p=0.85,
            max_tokens=MAX_OUTPUT,
        )
        answer = result["choices"][0]["message"]["content"] or ""
        return {
            "id": result.get("id"),
            "app_id": body.app_id,
            "answer": answer.strip(),
            "usage": result.get("usage", {}),
        }
    except Exception as exc:
        # Do not expose internal paths, prompts, or stack traces to app users.
        raise HTTPException(status_code=500, detail="SHOHIN AI could not generate a reply") from exc
