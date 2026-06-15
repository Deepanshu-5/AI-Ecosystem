# check_memory.py

import chromadb

client = chromadb.PersistentClient(
    path=r"D:\ai-ecosystem\vectordb"
)

print(
    client.list_collections()
)