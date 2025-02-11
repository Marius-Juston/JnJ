import json
import threading
from collections.abc import Callable
from typing import Optional, Type, List, Any

from langchain_core.messages import AIMessage, SystemMessage, HumanMessage
from langchain_core.prompts import PromptTemplate
from langchain_core.runnables.utils import Output
from langchain_core.tools import StructuredTool
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
            num_predict=self.config['num_predict'],
            mirostat=self.config['mirostat'],
            repeat_last_n=self.config['repeat_last_n'],
        )

        for parent in ('systems', 'templates'):
            for system_prompt in self.config[parent]:
                self.load(system_prompt, parent)

    def load(self, system, parent):
        with open(f"config/{self.config[parent][system]}", 'r', encoding="utf8") as f:
            self.config[parent][system] = f.read()

    async def astream(self, system_key: str, human_input: str, early_termination: Optional[threading.Event] = None,
                      context: Optional[str] = None, tool_choice: Optional[str] = None):

        llm, messages = self.setup_input(system_key, human_input, context, tool_choice)

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
               context: Optional[str] = None, tools: Optional[List[Type[Callable]]] = None,
               tool_choice: Optional[str] = None):

        llm, messages = self.setup_input(system_key, human_input, context, tools, tool_choice)

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
               context: Optional[str] = None, tools: Optional[List[Type[Callable]]] = None,
               tool_choice: Optional[str] = None) -> Output:
        llm, messages = self.setup_input(system_key, human_input, context, tools, tool_choice)

        return llm.invoke(messages)

    async def ainvoke(self, system_key: str, human_input: str,
                      context: Optional[str] = None, tools: Optional[List[Type[Callable]]] = None,
                      tool_choice: Optional[str] = None) -> Output:
        llm, messages = self.setup_input(system_key, human_input, context, tools, tool_choice)

        return await llm.ainvoke(messages)

    def setup_input(self, system_key: str, human_input: str, context: Optional[str] = None,
                    tools: Optional[List[Type[Callable]]] = None, tool_choice: Optional[str] = None):
        if tools is not None:
            llm = self.llm.bind_tools(tools, tool_choice=tool_choice)
        else:
            llm = self.llm

        if context:
            prompt_template = PromptTemplate(input_variables=['context', 'human_input'],
                                             template=self.config['templates'][system_key])
            human_input = prompt_template.format(context=context, human_input=human_input)

        messages = [
            SystemMessage(self.config['systems'][system_key]),
            HumanMessage(human_input)
        ]

        return llm, messages


def parse_tool_call(response: AIMessage, *tools: StructuredTool) -> List[Any]:
    tools_dict = {func.name: func for func in tools}

    outputs = []

    for tool_call in response.tool_calls:
        selected_tool = tools_dict[tool_call["name"].lower()]
        tool_output = selected_tool.invoke(tool_call["args"])
        outputs.append(tool_output)

    return outputs


if __name__ == '__main__':
    instance = LLM()
    instance2 = LLM()
    instance2 = LLM()

    for ch in instance.stream("lore", "Death dungeon"):
        print("---------------------------------", ch, "---------------------------------", )
