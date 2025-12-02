# message_builder.py
from typing import List, Dict

from .token_estimator import TokenEstimator
from .config import TOKEN_ESTIMATE_BUFFER

class MessageBuilder:
    @staticmethod
    def build_messages(history: List[Dict[str, str]], model: str, max_tokens: int, system_prompt: str) -> List[Dict[str, str]]:
        context_window = TokenEstimator.get_context_window(model)
        system_msg = {"role": "system", "content": system_prompt}
        messages = [system_msg] + history[:]
        estimated = TokenEstimator.estimate_prompt_tokens(messages)
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
                estimated = TokenEstimator.estimate_prompt_tokens(messages)
        return messages
