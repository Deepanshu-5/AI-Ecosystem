# delete_memory.py

import chromadb

client = chromadb.PersistentClient(
    path=r"D:\ai-ecosystem\vectordb"
)

try:
    client.delete_collection(
        "memory_base"
    )
    print("deleted")

except Exception as e:
    print(e)