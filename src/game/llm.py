import json
import threading
from collections.abc import Callable
from typing import Optional, Type, List

from langchain_core.prompts import PromptTemplate
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
            num_ctx=self.config['context_window'],
        )

        for parent in ('systems', 'templates'):
            for system_prompt in self.config[parent]:
                self.load(system_prompt, parent)

    def load(self, system, parent):
        with open(f"config/{self.config[parent][system]}", 'r') as f:
            self.config[parent][system] = f.read()

    async def astream(self, system_key: str, human_input: str, early_termination: Optional[threading.Event] = None,
                      context: Optional[str] = None):

        llm, messages = self.setup_input(system_key, human_input, context)

        chunks = ''

        async for chunk in self.llm.astream(messages):
            message = chunk.content

            if len(chunks) + len(message) > self.config['max_message_length']:

                index = chunks.rfind('\n')

                if index != -1:
                    message = chunks[index:] + message
                    chunks = chunks[:index]

                yield chunks
                chunks = ''

            chunks += message

            if early_termination and early_termination.is_set():
                yield chunks
                chunks = ''
                break

        if chunks:
            yield chunks

    def stream(self, system_key: str, human_input: str, early_termination: Optional[threading.Event] = None,
               context: Optional[str] = None, tools: Optional[List[Type[Callable]]] = None):

        llm, messages = self.setup_input(system_key, human_input, context, tools)

        chunks = ''

        for chunk in llm.stream(messages):
            message = chunk.content

            if len(chunks) + len(message) > self.config['max_message_length']:

                index = chunks.rfind('\n')

                if index != -1:
                    message = chunks[index:] + message
                    chunks = chunks[:index]

                yield chunks
                chunks = ''

            chunks += message

            if early_termination and early_termination.is_set():
                yield chunks
                chunks = ''
                break

        if chunks:
            yield chunks

    def invoke(self, system_key: str, human_input: str,
               context: Optional[str] = None, tools: Optional[List[Type[Callable]]] = None):
        llm, messages = self.setup_input(system_key, human_input, context, tools)

        return llm.invoke(messages)

    def setup_input(self, system_key: str, human_input: str, context: Optional[str] = None,
                    tools: Optional[List[Type[Callable]]] = None):
        if tools is not None:
            llm = self.llm.bind_tools(tools)
        else:
            llm = self.llm

        if context:
            prompt_template = PromptTemplate(input_variables=['context', 'human_input'],
                                             template=self.config['templates'][system_key])
            human_input = prompt_template.format(context=context, human_input=human_input)

        messages = [
            (
                "system", self.config['systems'][system_key],
            ),
            ("human", human_input)
        ]

        print(messages)

        return llm, messages


if __name__ == '__main__':
    instance = LLM()
    instance2 = LLM()
    instance2 = LLM()

    for ch in instance.stream("lore", "Death dungeon"):
        print("---------------------------------", ch, "---------------------------------", )
