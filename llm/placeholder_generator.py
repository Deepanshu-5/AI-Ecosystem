from llm.base_generator import BaseGenerator


class PlaceholderGenerator(
    BaseGenerator
):

    def generate(
        self,
        prompt: str
    ) -> str:

        print(
            "\n===== FINAL PROMPT =====\n"
        )

        print(prompt)

        return (
            "Generator placeholder"
        )