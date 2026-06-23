import sys
from pathlib import Path
import os

root = str(
    Path(__file__).resolve().parent.parent
)

if root not in sys.path:
    sys.path.insert(0, root)

from llm.rag import create_rag_prompt

def main():

    question = input(
        "\nAsk Question: "
    )

    answer = create_rag_prompt(question)

    print("\n===== ANSWER =====\n")

    print(answer)


if __name__ == "__main__":
    main()