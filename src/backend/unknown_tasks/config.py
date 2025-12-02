DEFAULT_MODEL = "openai/gpt-oss-20b"  # Valid Groq model with large context
DEFAULT_MAX_TOKENS = 1000
DEFAULT_TEMPERATURE = 0.7
DEFAULT_MAX_RETRIES = 3  # Default value if not in env
BACKOFF_BASE_SECONDS = 1.0  # Default value if not in env
TOKEN_ESTIMATE_BUFFER = 500  # Safety buffer for token estimates

# Model-specific context windows (from https://console.groq.com/docs/models)
MODEL_CONTEXT_WINDOWS = {
    "llama-3.1-8b-instant": 131072,
    "llama-3.3-70b-versatile": 131072,
    "meta-llama/llama-guard-4-12b": 131072,
    "openai/gpt-oss-120b": 131072,
    "openai/gpt-oss-20b": 131072,
    "groq/compound": 131072,
    "groq/compound-mini": 131072
}