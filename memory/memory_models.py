from dataclasses import dataclass, field
from datetime import datetime
from dataclasses import field

@dataclass
class Memory:

    content: str

    

    timestamp: str = field(
    default_factory=lambda: datetime.now().isoformat()
)

    score: float = 0.0