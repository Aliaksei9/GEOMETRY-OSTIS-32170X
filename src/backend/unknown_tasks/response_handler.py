# response_handler.py
from typing import Dict

class ResponseHandler:
    @staticmethod
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

    @staticmethod
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