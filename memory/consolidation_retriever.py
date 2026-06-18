from memory.memory_retriever import (
    retrieve_related_memories
)


def retrieve_project_cluster():

    results = retrieve_related_memories(
        query="AI ecosystem",
        top_k=10
    )

    filtered_documents = []

    CONSOLIDATED_PHRASES = [
        "efficient resource management",
        "system interoperability"
    ]

    for document in results["documents"]:

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

    return {
        "documents": filtered_documents
    }