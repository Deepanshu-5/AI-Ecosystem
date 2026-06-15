from dataclasses import dataclass
from datetime import datetime


@dataclass
class Memory:

    content: str

    timestamp: str = (
        datetime.now().isoformat()
    )

    score: float = 0.0