def build_prompt(
    question: str,
    context: str
):

    return f"""
You are a retrieval assistant.

Answer only from the supplied context.

If the answer is not found in the context,
say:

"I could not find the answer in the provided context."

Context:

{context}

Question:
{question}

Answer:
"""