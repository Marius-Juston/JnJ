import json
import functools

from langchain_ollama import ChatOllama


class LLM:
    def __new__(cls):
        if not hasattr(cls, 'instance'):
            cls.instance = super(LLM, cls).__new__(cls)
        return cls.instance

    def __init__(self, config='llm_config.json'):
        if hasattr(self, 'config'):
            return

        with open(f"config/{config}", 'r') as f:
            self.config = json.load(f)

        self.llm = ChatOllama(
            model=self.config['model'],
        )

        for system_prompt in self.config['systems']:
            self.load(system_prompt)

    def load(self, system):
        with open(f"config/{self.config['systems'][system]}", 'r') as f:
            self.config['systems'][system] = f.read()

    async def astream(self, system_key: str, human_input: str):
        messages = [
            (
                "system", self.config['systems'][system_key],
            ),
            ("human", human_input)
        ]

        chunks = ''

        async for chunk in self.llm.astream(messages):
            message = chunk.content

            if len(chunks) + len(message) > self.config['max_message_length']:
                yield chunks
                chunks = ''

            chunks += message

        if chunks:
            yield chunks


if __name__ == '__main__':
    instance = LLM()
    instance2 = LLM()
    instance2 = LLM()
