import re

def compress_context(context: str, max_chars: int = 4000) -> str:
    if len(context) <= max_chars:
        return context

    # Cut at last space before max_chars to avoid mid-word split
    truncated = context[:max_chars]
    last_space = truncated.rfind(" ")

    if last_space > max_chars * 0.8:
        return truncated[:last_space].rstrip() + " [...]"

    return truncated + " [...]"