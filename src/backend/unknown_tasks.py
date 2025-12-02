#!/usr/bin/env python3
"""
API server using FastAPI that integrates the Groq chat logic.
Receives POST requests with {"message": "user input"}, processes with Groq LLM,
and returns {"response": "assistant response"}.
Handles /reset to clear history.
Global history for simplicity (single session).
Run with: uvicorn this_file:app --reload
Requires: pip install fastapi uvicorn groq
"""
import os
import time
from typing import List, Dict, Optional
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from groq import Groq
from fastapi.middleware.cors import CORSMiddleware

from dotenv import load_dotenv
from pathlib import Path
load_dotenv(dotenv_path=Path(__file__).parent / ".env")

# --- Defaults / config ---
DEFAULT_MODEL = "openai/gpt-oss-20b" # Valid Groq model with large context
DEFAULT_MAX_TOKENS = 1000
DEFAULT_TEMPERATURE = 0.7
DEFAULT_MAX_RETRIES = int(os.environ.get("GROQ_MAX_RETRIES", 3))
BACKOFF_BASE_SECONDS = float(os.environ.get("GROQ_BACKOFF_BASE", 1.0))
TOKEN_ESTIMATE_BUFFER = 500 # Safety buffer for token estimates
# Model-specific context windows
MODEL_CONTEXT_WINDOWS = {
    "llama-3.1-8b-instant": 131072,
    "llama-3.3-70b-versatile": 131072,
    "meta-llama/llama-guard-4-12b": 131072,
    "openai/gpt-oss-120b": 131072,
    "openai/gpt-oss-20b": 131072,
    "groq/compound": 131072,
    "groq/compound-mini": 131072
}
# System prompt
SYSTEM_PROMPT_DEFAULT = """
    Ты ассистент по геометрии. ТЫ должен подсказывать ТОЛЬКО ПЕРВЫЙ БЛИЖАЙШИЙ СЛЕДУЮЩИЙ шаг в решении задач. НЕЛЬЗЯ называть сразу ответ. Упор делать на приведение нужных для решения задач теорем и аксиом. Все подсчёты, составление уравнений и формул ОСТАВИТЬ USER.
    Система должна перепроверять подсчёты USER. При ошибках система должна ответить: "Ошибка в подсчётах. ПЕРЕСЧИТАЙ."
    ИЗНАЧАЛЬНО ВСЕГДА ОГРАНИЧИВАТЬСЯ НАЗВАНИЕМ ТЕОРЕМЫ АКСИОМЫ И МЕСТОМ ЕЁ ПРИМЕНЕНИЯ И ЛИШЬ ПРИ ДАЛЬНЕЙШИХ РАСПРОСАХ ОТ ПОЛЬЗОВАТЕЛЯ ПРИВОДИТЬ УТОЧНЕНИЯ. МИНИМИЗИРОВАТЬ ЛЮБЫЕ РАСЧЁТЫ. ВСЕ ИХ ОСТАВЛЯТЬ НА ПОЛЬЗОВАТЕЛЯ И ЛИШЬ ПЕРЕПРОВЕРЯТЬ ЕГО ОТВЕТЫ.
    user: В равнобедренном треугольнике MNK (KM = KN) проведена биссектриса KE, равная 24 см. Периметр треугольника KEN равен 56 см. Найдите периметр треугольника MNK.
    system: Вспомним Теорему о свойстве биссектрисы равнобедренного треугольника, которая гласит следующее. В равнобедренном треугольнике биссектриса, проведенная к основанию, является его медианой и высотой. Эту теорему можно применить к биссектрисе KE.
    user: Из теоремы следует, что КЕ — высота. Но что это даёт?
    system: В контексте данной задачи нас интересует то, что KE — медиана.
    user: Если KE — медиана, тогда ME=EN. Тогда можно записать, что периметр треугольника MNK = KN+EN+ME+KM=KN+2EN+KM. А периметр треугольника KEN=KE+KN+EN. Зная периметр треугольника KEN и биссектрису KE мы можем найти сумму KN+EN=32. Но что дальше?
    system: Треугольник MNK равнобедренный, значит KN+KM можно приравнять к 2KN.
    user: И тогда периметр треугольника MNK = 2KN+2EN=2(KN+EN)=2*32=62.
    system: Ошибка в подсчётах. ПЕРЕСЧИТАЙ.
    user: Периметр треугольника MNK = 64
    system: Правильно
    Пример 2:
    user: В треугольнике MNK проведена биссектриса ME. Известно, что ∠ MKN + ∠ NME = ∠ MNK + ∠ KME, KE = 4 см, MN = 9 см. Найдите периметр треугольника MNK.
    system: Так как ME — биссектриса, то угол NME равен углу KME. С учётом этого нужно посмотреть на выражение ∠ MKN + ∠ NME = ∠ MNK + ∠ KME ещё раз.
    user: Получается угол MKN = углу MNK. Но что нам это даёт.
    system: Вспомни признак равнобедренного треугольника: если в треугольнике два угла равны, то он равнобедренный.
    user: Если треугольник MNK равнобедренный, значит MN=MK=9 см.Но мы ещё не знаем NK.
    system: Вспомним Теорему о свойстве биссектрисы равнобедренного треугольника, которая гласит следующее. В равнобедренном треугольнике биссектриса, проведенная к основанию, является его медианой и высотой. Эту теорему можно применить к биссектрисе ME.
    user: Тогда NE=KE. А NK=NE+KE. Значит NK=2*KE=8 см. А весь периметр треугольника MNK равен MN+MK+KE=26 см.
    system: Правильно
    Все ответы должны быть в простом тексте без LaTeX форматирования. Не используй символы вроде (, ), {, } для чисел или формул. Для десятичных дробей используй точку (.), а не запятую (,). Для единиц измерения просто пиши 'см' без специального форматирования.
    """
SYSTEM_PROMPT = os.environ.get("GROQ_SYSTEM_PROMPT", SYSTEM_PROMPT_DEFAULT)
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
class KeyManager:
    def __init__(self, keys: List[str]):
        self.keys = [{"key": k, "status": "ok"} for k in keys]
        self.index = 0
    def get_current(self) -> Optional[str]:
        if not self.keys:
            return None
        n = len(self.keys)
        for i in range(n):
            idx = (self.index + i) % n
            if self.keys[idx]["status"] == "ok":
                self.index = idx
                return self.keys[idx]["key"]
        return None
    def rotate_to_next(self):
        n = len(self.keys)
        for i in range(1, n + 1):
            idx = (self.index + i) % n
            self.index = idx
            if self.keys[idx]["status"] == "ok":
                return self.keys[idx]["key"]
        return None
    def mark_blocked(self, key: str):
        for k in self.keys:
            if k["key"] == key:
                k["status"] = "blocked"
                break
# ----------------- Error detection -----------------
def is_blocked_api_access_error(exc: Optional[Exception], resp_data: Optional[dict]) -> bool:
    if exc:
        s = str(exc).lower()
        status = getattr(exc, "status_code", None) or getattr(getattr(exc, "response", None), "status_code", None)
        if status == 400 or "blocked_api_access" in s or "api calls from any key in your organization" in s:
            return True
    if isinstance(resp_data, dict):
        err = resp_data.get("error")
        if isinstance(err, dict):
            code = (err.get("code") or "").lower()
            msg = (err.get("message") or "").lower()
            if "blocked_api_access" in code or "blocked_api_access" in msg:
                return True
    return False
def is_rate_limit_exception(exc: Exception) -> bool:
    s = str(exc).lower()
    status = getattr(exc, "status_code", None) or getattr(getattr(exc, "response", None), "status_code", None)
    if status == 429 or "429" in s or "rate limit" in s or "too many requests" in s:
        return True
    return False
def is_context_length_exceeded(exc: Exception) -> bool:
    s = str(exc).lower()
    status = getattr(exc, "status_code", None) or getattr(getattr(exc, "response", None), "status_code", None)
    if status == 400 and ("context_length_exceeded" in s or "maximum context length" in s or "tokens. however, your messages resulted in" in s):
        return True
    return False
def extract_retry_after(exc: Exception) -> Optional[int]:
    resp = getattr(exc, "response", None)
    if resp:
        headers = getattr(resp, "headers", {})
        ra = headers.get("Retry-After") or headers.get("retry-after")
        if ra:
            try:
                return int(ra)
            except ValueError:
                pass
    return None
def normalize_response(resp) -> Dict:
    if resp is None:
        return {}
    if isinstance(resp, dict):
        return resp
    if hasattr(resp, "to_dict"):
        try:
            return resp.to_dict()
        except Exception:
            pass
    try:
        return dict(resp.__dict__)
    except Exception:
        return {"raw": str(resp)}
def extract_assistant_text(response_data: Dict) -> str:
    choices = response_data.get("choices")
    if choices and isinstance(choices, list) and len(choices) > 0:
        first = choices[0]
        if isinstance(first, dict):
            msg = first.get("message") or {}
            if isinstance(msg, dict):
                return msg.get("content") or first.get("text") or ""
            return str(msg) or first.get("text") or ""
        else:
            return str(first)
    return response_data.get("text") or response_data.get("output") or response_data.get("raw", "") or ""
# ----------------- Token estimation and message building -----------------
def estimate_tokens(text: str) -> int:
    return len(text) // 4 + 1
def estimate_prompt_tokens(messages: List[Dict[str, str]]) -> int:
    content_tokens = sum(estimate_tokens(m["content"]) for m in messages)
    overhead = 4 * len(messages)
    return content_tokens + overhead
def get_context_window(model: str) -> int:
    return MODEL_CONTEXT_WINDOWS.get(model, 8192)
def build_messages(history: List[Dict[str, str]], model: str, max_tokens: int) -> List[Dict[str, str]]:
    context_window = get_context_window(model)
    system_msg = {"role": "system", "content": SYSTEM_PROMPT}
    messages = [system_msg] + history[:]
    estimated = estimate_prompt_tokens(messages)
    max_allowed = context_window - max_tokens - TOKEN_ESTIMATE_BUFFER
    if estimated > max_allowed:
        truncated_history = history[:]
        while estimated > max_allowed and len(truncated_history) > 1:
            if truncated_history and truncated_history[0]["role"] == "user":
                truncated_history.pop(0)
                if truncated_history and truncated_history[0]["role"] == "assistant":
                    truncated_history.pop(0)
            else:
                truncated_history.pop(0)
            messages = [system_msg] + truncated_history
            estimated = estimate_prompt_tokens(messages)
    return messages
# ----------------- API Setup -----------------
app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins, or specify your frontend origin e.g., ["http://localhost:3000"]
    allow_credentials=True,
    allow_methods=["*"],  # Allow all methods, including OPTIONS
    allow_headers=["*"],  # Allow all headers
)

class ChatRequest(BaseModel):
    message: str
# Global history (for single session; use sessions for multi-user)
history: List[Dict[str, str]] = []
keys = parse_keys_from_env()
if not keys:
    raise ValueError("No API keys found in GROQ_API_KEYS or GROQ_API_KEY")
km = KeyManager(keys)
model = DEFAULT_MODEL
max_tokens = DEFAULT_MAX_TOKENS
temperature = DEFAULT_TEMPERATURE
max_retries = DEFAULT_MAX_RETRIES
@app.post("/chat")
async def chat_endpoint(req: ChatRequest):
    global history
    user = req.message.strip()
    if not user:
        raise HTTPException(status_code=400, detail="Empty message")
    if user == "/reset":
        history.clear()
        return {"response": "[История очищена]"}
    history.append({"role": "user", "content": user})
    current_key = km.get_current()
    if not current_key:
        raise HTTPException(status_code=503, detail="No available API keys")
    attempt = 0
    resp_data = None
    truncated = False
    while attempt <= max_retries:
        messages = build_messages(history, model, max_tokens)
        payload = {
            "messages": messages,
            "model": model,
            "max_tokens": max_tokens,
            "temperature": temperature,
        }
        client = Groq(api_key=current_key)
        try:
            resp = client.chat.completions.create(**payload)
            resp_data = normalize_response(resp)
            if is_blocked_api_access_error(None, resp_data):
                km.mark_blocked(current_key)
                current_key = km.rotate_to_next()
                if not current_key:
                    raise HTTPException(status_code=503, detail="All API keys blocked")
                attempt = 0
                continue
            break
        except Exception as e:
            if is_blocked_api_access_error(e, None):
                km.mark_blocked(current_key)
                current_key = km.rotate_to_next()
                if not current_key:
                    raise HTTPException(status_code=503, detail="All API keys blocked")
                attempt = 0
                continue
            if is_context_length_exceeded(e):
                if not truncated:
                    history = history[len(history) // 2 :]
                    truncated = True
                    continue
                else:
                    raise HTTPException(status_code=400, detail="Context length exceeded after truncation")
            if is_rate_limit_exception(e):
                attempt += 1
                ra = extract_retry_after(e)
                wait_time = ra if ra else BACKOFF_BASE_SECONDS * (2 ** (attempt - 1))
                time.sleep(wait_time)
                if attempt > max_retries:
                    km.mark_blocked(current_key)
                    current_key = km.rotate_to_next()
                    if not current_key:
                        raise HTTPException(status_code=503, detail="All API keys blocked")
                    attempt = 0
                continue
            raise HTTPException(status_code=500, detail=f"API error: {str(e)}")
    if resp_data is None:
        raise HTTPException(status_code=500, detail="No response from API")
    assistant_text = extract_assistant_text(resp_data)
    if not assistant_text.strip():
        raise HTTPException(status_code=500, detail="Empty response from API")
    history.append({"role": "assistant", "content": assistant_text})
    return {"response": assistant_text}
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)