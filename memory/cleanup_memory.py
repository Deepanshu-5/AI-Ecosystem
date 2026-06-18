import sys
from pathlib import Path

root = str(
    Path(__file__).resolve().parent.parent
)

if root not in sys.path:
    sys.path.insert(0, root)

from memory.memory_store import (
    collection
)

data = collection.get()

bad_ids = []

for doc_id, doc in zip(
    data["ids"],
    data["documents"]
):

    text = doc.lower()

    if (
    "no conversation content" in text
    or "summary: none" in text
    or "conversation content not provided" in text
):
        bad_ids.append(
            doc_id
        )

if bad_ids:

    collection.delete(
        ids=bad_ids
    )

print(
    f"Removed {len(bad_ids)} bad memories"
)