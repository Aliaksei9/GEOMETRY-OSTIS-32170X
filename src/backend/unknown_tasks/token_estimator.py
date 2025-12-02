from typing import List, Dict

from .config import MODEL_CONTEXT_WINDOWS

class TokenEstimator:
    @staticmethod
    def estimate_tokens(text: str) -> int:
        return len(text) // 2 + 1

    @staticmethod
    def estimate_prompt_tokens(messages: List[Dict[str, str]]) -> int:
        content_tokens = sum(TokenEstimator.estimate_tokens(m["content"]) for m in messages)
        overhead = 4 * len(messages)
        return content_tokens + overhead

    @staticmethod
    def get_context_window(model: str) -> int:
        return MODEL_CONTEXT_WINDOWS.get(model, 8192)
