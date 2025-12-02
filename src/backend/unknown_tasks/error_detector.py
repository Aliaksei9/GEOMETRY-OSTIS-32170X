# error_detector.py
from typing import Optional, Dict

class ErrorDetector:
    @staticmethod
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

    @staticmethod
    def is_rate_limit_exception(exc: Exception) -> bool:
        s = str(exc).lower()
        status = getattr(exc, "status_code", None) or getattr(getattr(exc, "response", None), "status_code", None)
        if status == 429 or "429" in s or "rate limit" in s or "too many requests" in s:
            return True
        return False

    @staticmethod
    def is_context_length_exceeded(exc: Exception) -> bool:
        s = str(exc).lower()
        status = getattr(exc, "status_code", None) or getattr(getattr(exc, "response", None), "status_code", None)
        if status in (400, 413) and ("context_length_exceeded" in s or "maximum context length" in s or "tokens. however, your messages resulted in" in s or "request body is too large" in s or "request too large" in s):
            return True
        return False

    @staticmethod
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