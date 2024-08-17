import json
import os
from typing import Any

from langchain_ollama import ChatOllama
from typing_extensions import override

from game.llm import LLM
from game.player import player_


def player_info(class_name: str, race_name: str, background_lore: str) -> bool:
    """This function is meant to save the player information for the Dungeon and Dragon game.

    Args:
        class_name: (str) The DnD class of the character
        race_name: () The DnD race of the character.
        background_lore: (str) The detailed and comprehensive background lore of the character..
    """
    return True


def test_player_prompt():
    tools = [player_info]

    tools_dict = {func.__name__: func for func in tools}

    llm = ChatOllama(
        model="mistral-nemo",
        temperature=0,
    ).bind_tools(tools)

    result = llm.invoke(
        "Could you validate user 123? They previously lived at "
        "123 Fake St in Boston MA and 234 Pretend Boulevard in "
        "Houston TX."
    )

    for tool in result.tool_calls:
        result = tools_dict[tool['name']](**tool['args'])
        print(result)


def test_lore_prompt():
    with open("config/llm_config.json", 'r') as f:
        config = json.load(f)

    with open(f"config/{config['systems']['lore']}", 'r') as f:
        system_prompt = f.read()

    print(system_prompt)

    llm = ChatOllama(
        model="mistral-nemo",
        temperature=0,
    )

    messages = [
        (
            "system", system_prompt
        ),
        ("human", "Sci-fi Miniaturization War")
    ]

    chunks = ''

    for chunk in llm.stream(messages):
        message = chunk.content

        if len(chunks) + len(message) > config['max_message_length']:
            print(chunks, end='')
            chunks = ''

        chunks += message

    if chunks:
        print(chunks, end='')

def user_design(override=False):
    llm = LLM()

    lore_file = 'test/context.txt'

    if not override and os.path.exists(lore_file):
        with open(lore_file, 'r') as f:
            lore = f.read()
    else:
        lore = ''

        for message_chunk in llm.stream('lore', 'Sci-fi'):
            lore += message_chunk
    lore = lore.strip()

    print(lore)


    player = """
Character Name: Marius
Character Background Lore: 
Class Name: 
Race Name: 
    """.strip()

    result = llm.invoke('character_creation', player, context=lore, tools=[player_] )

    print(result.content)
    print(result.tool_calls[0]['args'])


if __name__ == '__main__':
    user_design(override=True)
