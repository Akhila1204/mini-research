import os
from pathlib import Path
from dotenv import load_dotenv

# Ensure .env is loaded regardless of current working directory
env_path = Path(__file__).resolve().parent.parent / ".env"
load_dotenv(dotenv_path=env_path)

from typing import List, Optional

class Config:
    HOST: str = os.getenv("HOST", "127.0.0.1")
    PORT: int = int(os.getenv("PORT") or 8000)
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")
    TAVILY_API_KEY: str = os.getenv("TAVILY_API_KEY", "")
    SERPAPI_API_KEY: str = os.getenv("SERPAPI_API_KEY", "")
    DEFAULT_MODEL: str = os.getenv("GEMINI_MODEL", "gemini-3.5-flash-lite")

SUPPORTED_FLASH_MODELS: List[str] = [
    "gemini-3.5-flash-lite",
    "gemini-3.5-flash",
    "gemini-3.6-flash",
    "gemini-3.7-flash",
    "gemini-3.8-flash",
]

def get_fallback_chain(primary_model: Optional[str] = None) -> List[str]:
    """
    Returns an ordered list of Gemini models to attempt with seamless redirection.
    If a model is unavailable (e.g., 503 high demand spike, 429 quota/rate limit),
    the system redirects to the next candidate model in the chain.
    """
    target = (primary_model or os.getenv("GEMINI_MODEL") or "gemini-3.6-flash").strip().lower()
    if target == "gemini-2.5-flash":
        target = "gemini-3.6-flash"

    priority_order = {
        "gemini-3.6-flash": ["gemini-3.5-flash-lite", "gemini-3.5-flash", "gemini-3.6-flash", "gemini-3.7-flash", "gemini-3.8-flash"],
        "gemini-3.7-flash": ["gemini-3.5-flash-lite", "gemini-3.7-flash", "gemini-3.8-flash", "gemini-3.6-flash", "gemini-3.5-flash"],
        "gemini-3.8-flash": ["gemini-3.5-flash-lite", "gemini-3.8-flash", "gemini-3.7-flash", "gemini-3.6-flash", "gemini-3.5-flash"],
        "gemini-3.5-flash": ["gemini-3.5-flash-lite", "gemini-3.5-flash", "gemini-3.6-flash", "gemini-3.8-flash", "gemini-3.7-flash"],
        "gemini-3.5-flash-lite": ["gemini-3.5-flash-lite", "gemini-3.5-flash", "gemini-3.6-flash", "gemini-3.7-flash", "gemini-3.8-flash"],
    }

    if target in priority_order:
        return list(priority_order[target])

    chain = [target] if target else []
    for m in SUPPORTED_FLASH_MODELS:
        if m not in chain:
            chain.append(m)
    return chain

config = Config()

