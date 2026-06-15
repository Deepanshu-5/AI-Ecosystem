from dataclasses import dataclass
from typing import Optional


@dataclass
class RetrievedChunk:
    text: str
    source: str
    chunk_id: int
    score: Optional[float] = None