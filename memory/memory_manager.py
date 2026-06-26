import sys
from pathlib import Path

root = str(
    Path(__file__).resolve().parent.parent
)

if root not in sys.path:
    sys.path.insert(0, root)

from memory.chat_summarizer import (
    summarize_chat
)

from memory.memory_service import (
    remember
)

from memory.memory_filter import (
    is_valid_memory
)

import time
def process_conversation(chat_text: str):
    start = time.time()
    summary = summarize_chat(chat_text)
    summary_time = time.time()

    if summary.strip() == "NO_MEMORY":
      return None

    print(
    f"[TIME] Summarization: {summary_time - start:.2f}s"
)
    
    if is_valid_memory(summary):
        
      remember(summary)
      remember_time = time.time()

      print(
    f"[TIME] Remember: {remember_time - summary_time:.2f}s"
)
      
      from memory.consolidation_service import (should_consolidate,build_consolidation_plan)
      consolidation_start = time.time()
      if should_consolidate():

        plan = build_consolidation_plan()

        print(
            "\n[CONSOLIDATION TRIGGERED]"
        )

        print(
            f"Source Memories: {plan['source_count']}"
        )

        print(
            f"Summary:\n{plan['summary']}"
        )
        consolidation_end = time.time()

        print(
    f"[TIME] Consolidation: {consolidation_end - consolidation_start:.2f}s"
)
    return summary
