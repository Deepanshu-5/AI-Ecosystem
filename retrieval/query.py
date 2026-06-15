import sys
from pathlib import Path
import os

print(os.getcwd())
root = str(
    Path(__file__).resolve().parent.parent
)

if root not in sys.path:
    sys.path.insert(0, root)

from llm.rag import create_rag_prompt
from llm.generator import PlaceholderGenerator
from retrieval.retriever import retrieve


def main():

    question = input(
        "\nAsk Question: "
    )

    prompt = create_rag_prompt(
        question
    )

    generator = PlaceholderGenerator()

    answer = generator.generate(prompt)

    print("\n===== ANSWER =====\n")

    print(answer)


if __name__ == "__main__":
    main()