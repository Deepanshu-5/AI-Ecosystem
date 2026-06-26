"""Token counter with multiple backends for accuracy.

Priority:
1. transformers AutoTokenizer (most accurate for local models)
2. tiktoken (if available, good for GPT-style models)
3. Calibrated character-based fallback (always works)

Usage:
    from shared.token_counter import token_counter
    count = token_counter.count(text)
"""

from __future__ import annotations

import warnings


class _TokenCounter:
    """Lazy-loading token counter that tries multiple backends."""

    def __init__(self):
        self._tokenizer = None
        self._backend = None
        self._calibration_factor = 3.2  # Conservative: chars per token

    def _load_backend(self):
        """Attempt to load the best available tokenizer backend."""
        if self._backend is not None:
            return

        # 1. Try transformers AutoTokenizer
        try:
            from transformers import AutoTokenizer

            # Use a lightweight public tokenizer that is already likely cached
            # or can be downloaded quickly.  "Qwen/Qwen2.5-1.5B-Instruct" matches
            # the project's default model.  If it is not available, any
            # SentencePiece/Unigram tokenizer (e.g. Qwen family) is close enough
            # for budgeting purposes.
            self._tokenizer = AutoTokenizer.from_pretrained(
                "Qwen/Qwen2.5-1.5B-Instruct",
                trust_remote_code=True,
                use_fast=True,
            )
            self._backend = "transformers"
            return
        except Exception:
            pass

        # 2. Try tiktoken (common for OpenAI-style models, very fast)
        try:
            import tiktoken

            self._tokenizer = tiktoken.get_encoding("cl100k_base")
            self._backend = "tiktoken"
            return
        except Exception:
            pass

        # 3. Fallback to calibrated character-based counting
        self._backend = "fallback"
        warnings.warn(
            "[TOKEN COUNTER] No precise tokenizer available. "
            "Using calibrated character-based fallback. "
            "Install 'transformers' or 'tiktoken' for better accuracy.",
            stacklevel=2,
        )

    def count(self, text: str) -> int:
        """Return estimated token count for *text*."""
        if not text:
            return 0

        self._load_backend()

        if self._backend == "transformers":
            # Tokenizers return a dict with "input_ids";  len gives token count
            encoded = self._tokenizer(text, add_special_tokens=False)
            return len(encoded["input_ids"])

        if self._backend == "tiktoken":
            return len(self._tokenizer.encode(text))

        # Fallback: calibrated character heuristic with safety buffer
        # For mixed English/text, ~3.5–4.0 chars/token is typical.
        # We use 3.2 to be conservative (slightly overcount = safer budgets).
        return max(1, int(len(text) / self._calibration_factor))

    def count_batch(self, texts: list[str]) -> list[int]:
        """Return token counts for a list of texts."""
        if not texts:
            return []
        return [self.count(t) for t in texts]

    def truncate(self, text: str, max_tokens: int) -> str:
        """Truncate *text* to fit within *max_tokens*."""
        if max_tokens <= 0:
            return ""

        if self.count(text) <= max_tokens:
            return text

        self._load_backend()

        if self._backend == "transformers":
            encoded = self._tokenizer(text, add_special_tokens=False)
            input_ids = encoded["input_ids"]
            if len(input_ids) <= max_tokens:
                return text
            truncated_ids = input_ids[:max_tokens]
            return self._tokenizer.decode(
                truncated_ids, skip_special_tokens=True
            )

        if self._backend == "tiktoken":
            tokens = self._tokenizer.encode(text)
            if len(tokens) <= max_tokens:
                return text
            return self._tokenizer.decode(tokens[:max_tokens])

        # Fallback: approximate by characters
        max_chars = int(max_tokens * self._calibration_factor)
        truncated = text[:max_chars]
        # Avoid mid-word split if possible
        last_space = truncated.rfind(" ")
        if last_space > max_chars * 0.8:
            return truncated[:last_space].rstrip() + " [...]"
        return truncated.rstrip() + " [...]"


# Global singleton — same pattern as CacheService, ModelRegistry, etc.
token_counter = _TokenCounter()


def count_tokens(text: str) -> int:
    """Legacy compatibility wrapper."""
    return token_counter.count(text)
