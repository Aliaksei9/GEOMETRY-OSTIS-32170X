
import os
import asyncio
from typing import List, Dict
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from groq import AsyncGroq
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from pathlib import Path
import httpx

load_dotenv(dotenv_path=Path(__file__).parent / ".env")

from .config import (
    DEFAULT_MODEL, DEFAULT_MAX_TOKENS, DEFAULT_TEMPERATURE,
    DEFAULT_MAX_RETRIES, BACKOFF_BASE_SECONDS
)
from .prompt import SYSTEM_PROMPT_DEFAULT

# System prompt: читаем из окружения или используем дефолт из prompt.py
SYSTEM_PROMPT = os.environ.get("GROQ_SYSTEM_PROMPT", SYSTEM_PROMPT_DEFAULT)

# Импорты классов
from .key_manager import KeyManager
from .error_detector import ErrorDetector
from .message_builder import MessageBuilder
from .response_handler import ResponseHandler

# ---------------- Key management ----------------
def parse_keys_from_env() -> List[str]:
    v = os.environ.get("GROQ_API_KEYS") or os.environ.get("GROQ_API_KEY")
    if not v:
        return []
    keys = [k.strip() for k in v.split(",") if k.strip()]
    return keys

def mask_key(k: str) -> str:
    if not k:
        return "<empty>"
    if len(k) <= 8:
        return k[:2] + "..." + k[-2:]
    return k[:4] + "..." + k[-4:]

# ----------------- API Setup -----------------
app = FastAPI()
# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"], # Allow all origins, or specify your frontend origin e.g., ["http://localhost:3000"]
    allow_credentials=True,
    allow_methods=["*"], # Allow all methods, including OPTIONS
    allow_headers=["*"], # Allow all headers
)

# Shared HTTP client
async_client: httpx.AsyncClient = None

@app.on_event("startup")
async def startup_event():
    global async_client
    async_client = httpx.AsyncClient(timeout=60.0)  # Adjust timeout as needed

@app.on_event("shutdown")
async def shutdown_event():
    global async_client
    if async_client:
        await async_client.aclose()

class ChatRequest(BaseModel):
    message: str

# Global history (for single session; use sessions for multi-user)
history: List[Dict[str, str]] = []
history_lock = asyncio.Lock()
keys = parse_keys_from_env()
if not keys:
    raise ValueError("No API keys found in GROQ_API_KEYS or GROQ_API_KEY")
km = KeyManager(keys)
model = DEFAULT_MODEL
max_tokens = DEFAULT_MAX_TOKENS
temperature = DEFAULT_TEMPERATURE
max_retries = int(os.environ.get("GROQ_MAX_RETRIES", DEFAULT_MAX_RETRIES))
backoff_base_seconds = float(os.environ.get("GROQ_BACKOFF_BASE", BACKOFF_BASE_SECONDS))

@app.post("/chat")
async def chat_endpoint(req: ChatRequest):
    user = req.message.strip()
    if not user:
        raise HTTPException(status_code=400, detail="Empty message")
    if user == "/reset":
        async with history_lock:
            history.clear()
        return {"response": "[История очищена]"}
    async with history_lock:
        history.append({"role": "user", "content": user})
    current_key = await km.get_current()
    if not current_key:
        raise HTTPException(status_code=503, detail="No available API keys")
    attempt = 0
    resp_data = None
    truncated = False
    while attempt <= max_retries:
        async with history_lock:
            messages = MessageBuilder.build_messages(history, model, max_tokens, SYSTEM_PROMPT)
        payload = {
            "messages": messages,
            "model": model,
            "max_tokens": max_tokens,
            "temperature": temperature,
        }
        client = AsyncGroq(http_client=async_client, api_key=current_key)
        try:
            resp = await client.chat.completions.create(**payload)
            resp_data = ResponseHandler.normalize_response(resp)
            if ErrorDetector.is_blocked_api_access_error(None, resp_data):
                await km.mark_blocked(current_key)
                current_key = await km.rotate_to_next()
                if not current_key:
                    raise HTTPException(status_code=503, detail="All API keys blocked")
                attempt = 0
                continue
            break
        except Exception as e:
            if ErrorDetector.is_blocked_api_access_error(e, None):
                await km.mark_blocked(current_key)
                current_key = await km.rotate_to_next()
                if not current_key:
                    raise HTTPException(status_code=503, detail="All API keys blocked")
                attempt = 0
                continue
            if ErrorDetector.is_context_length_exceeded(e):
                if not truncated:
                    async with history_lock:
                        history[:] = history[len(history) // 2 :]
                    truncated = True
                    continue
                else:
                    raise HTTPException(status_code=400, detail="Context length exceeded after truncation")
            if ErrorDetector.is_rate_limit_exception(e):
                attempt += 1
                ra = ErrorDetector.extract_retry_after(e)
                wait_time = ra if ra else backoff_base_seconds * (2 ** (attempt - 1))
                await asyncio.sleep(wait_time)
                if attempt > max_retries:
                    await km.mark_blocked(current_key)
                    current_key = await km.rotate_to_next()
                    if not current_key:
                        raise HTTPException(status_code=503, detail="All API keys blocked")
                    attempt = 0
                continue
            raise HTTPException(status_code=500, detail=f"API error: {str(e)}")
    if resp_data is None:
        raise HTTPException(status_code=500, detail="No response from API")
    assistant_text = ResponseHandler.extract_assistant_text(resp_data)
    if not assistant_text.strip():
        raise HTTPException(status_code=500, detail="Empty response from API")
    async with history_lock:
        history.append({"role": "assistant", "content": assistant_text})
    return {"response": assistant_text}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
