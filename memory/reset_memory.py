# reset_memory.py

import chromadb

client = chromadb.PersistentClient(
    path=r"D:\ai-ecosystem\vectordb"
)

client.delete_collection(
    "memory_base"
)

client.create_collection(
    "memory_base"
)

print("memory reset")