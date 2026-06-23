import json
from pathlib import Path

# Load from settings.json if it exists, else use defaults
_SETTINGS_PATH = Path(__file__).parent / "settings.json"
_user_settings = {}
if _SETTINGS_PATH.exists():
    with open(_SETTINGS_PATH, "r", encoding="utf-8") as f:
        _user_settings = json.load(f)

CHROMA_PATH = _user_settings.get("chroma_path", r"D:\ai-ecosystem\vectordb")
COLLECTION_NAME = _user_settings.get("collection_name", "knowledge_base")
MEMORY_COLLECTION = _user_settings.get("memory_collection", "memory_base")
CHUNK_SIZE = _user_settings.get("chunk_size", 500)
CHUNK_OVERLAP = _user_settings.get("chunk_overlap", 100)
EMBEDDING_MODEL = _user_settings.get("embedding_model", "BAAI/bge-base-en-v1.5")
RERANK_TOP_K = _user_settings.get("rerank_top_k", 10)
FINAL_CONTEXT_CHUNKS = _user_settings.get("final_context_chunks", 2)
MIN_RERANK_SCORE = _user_settings.get("min_rerank_score", 3)
CHAT_MODEL = _user_settings.get(
    "chat_model",
    "qwen2.5:1.5b"
)

SUMMARY_MODEL = _user_settings.get(
    "summary_model",
    "qwen2.5:1.5b"
)
SUMMARY_THRESHOLD = _user_settings.get("summary_threshold", 100)
RECENT_KEEP = _user_settings.get("recent_keep", 5)