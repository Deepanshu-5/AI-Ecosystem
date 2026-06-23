from memory.memory_retriever import (
    retrieve_related_memories
)


def retrieve_project_cluster():

    results = retrieve_related_memories(
        query="AI ecosystem",
        top_k=10
    )

    filtered_documents = []
    filtered_ids = []

    CONSOLIDATED_PHRASES = [
        "efficient resource management",
        "system interoperability"
    ]

    for memory_id, document in zip(
    results["ids"],
    results["documents"]
):

        is_consolidated = False

        document_lower = document.lower()

        for phrase in CONSOLIDATED_PHRASES:

            if phrase in document_lower:
                is_consolidated = True
                break

        if not is_consolidated:

            filtered_documents.append(
                document
            )
            filtered_ids.append(
                memory_id
            )

    return { "ids": filtered_ids,
        "documents": filtered_documents
    }