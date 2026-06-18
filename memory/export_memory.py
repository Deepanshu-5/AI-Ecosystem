import sys
from pathlib import Path

root = str(
    Path(__file__).resolve().parent.parent
)

if root not in sys.path:
    sys.path.insert(0, root)

import chromadb

from config.settings import (
    CHROMA_PATH
)

MEMORY_COLLECTION = "memory_base"

client = chromadb.PersistentClient(
    path=CHROMA_PATH
)

collection = client.get_collection(
    MEMORY_COLLECTION
)

data = collection.get()

print("\n===== MEMORY COUNT =====")
print(len(data["documents"]))

print("\n===== MEMORY IDS =====")
for memory_id in data["ids"]:
    print(memory_id)

print("\n===== MEMORY DOCUMENTS =====")
for i, doc in enumerate(
    data["documents"],
    start=1
):
    print(f"\n[{i}]")
    print(doc)