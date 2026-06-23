import sys


def show_help():

    print("\nAvailable Commands:\n")

    print("python main.py ingest")
    print("python main.py query")
    print("python main.py consolidate")


def main():

    if len(sys.argv) < 2:
        show_help()
        return

    command = sys.argv[1].lower()

    if command == "ingest":

        from ingestion.ingest import main as ingest_main

        print("\n[INGESTION STARTED]\n")

        ingest_main()

        print("\n[INGESTION COMPLETE]\n")

    elif command == "query":

        from llm.rag import create_rag_prompt

        question = input(
            "\nQuestion: "
        )

        answer = create_rag_prompt(
            question
        )

        print(
            "\n===== ANSWER =====\n"
        )

        print(answer)

    elif command == "consolidate":

        from memory.consolidation_service import (
            build_consolidation_plan
        )

        result = (
            build_consolidation_plan()
        )

        print(
            "\n===== CONSOLIDATION =====\n"
        )

        print(
            f"Source Count: "
            f"{result['source_count']}"
        )

        print(
            "\nSummary:\n"
        )

        print(
            result["summary"]
        )

    else:

        print(
            f"\nUnknown command: "
            f"{command}\n"
        )

        show_help()


if __name__ == "__main__":
    main()