class CacheService:

    def __init__(self):
        self.cache = {}

    def get(self, question: str):
     return self.cache.get(
        question.strip().lower()
    )

    def set(self, question: str, result):
      self.cache[
        question.strip().lower()
    ] = result


cache = CacheService()