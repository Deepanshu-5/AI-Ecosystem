import sys
from pathlib import Path

root = str(
    Path(__file__).resolve().parent.parent
)

if root not in sys.path:
    sys.path.insert(0, root)

from memory.consolidation_service import (
    store_consolidated_memory
)


def consolidate():

    summary = store_consolidated_memory()

    print(
        "\n===== CONSOLIDATED MEMORY =====\n"
    )

    print(summary)


if __name__ == "__main__":
    consolidate()