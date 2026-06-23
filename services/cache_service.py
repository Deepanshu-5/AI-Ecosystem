import time


class CacheService:

    def __init__(
        self,
        max_size=1000,
        ttl=3600
    ):
        self.cache = {}
        self.max_size = max_size
        self.ttl = ttl

    def get(self, question: str):

        key = question.strip().lower()

        if key not in self.cache:
            return None

        value, timestamp = self.cache[key]

        if time.time() - timestamp > self.ttl:
            del self.cache[key]
            return None

        return value

    def set(
        self,
        question: str,
        result
    ):

        key = question.strip().lower()

        if len(self.cache) >= self.max_size:
            oldest = next(iter(self.cache))
            del self.cache[oldest]

        self.cache[key] = (
            result,
            time.time()
        )


cache = CacheService()