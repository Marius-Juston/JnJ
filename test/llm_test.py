import json
import os

from langchain_core.messages import SystemMessage, HumanMessage
from langchain_ollama import ChatOllama

from game.llm.dataclass import TimeEstimate
from game.llm.llm import LLM, parse_tool_call
from game.player import player_, Player


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
Character Name: Laura
Character Background Lore: 
Class Name: 
Race Name: 
    """.strip()

    result = llm.invoke('character_creation', player, context=lore, tools=[player_], tool_choice='player_')

    outputs = parse_tool_call(result, player_)

    print(result.content)
    print(result.tool_calls[0]['args'])
    print(outputs)

    class Temp:
        def __init__(self):
            self.display_name = "Marius"

    player = Player(Temp())

    print("---------------------------")
    class_name, race_name, background_lore, race_description, class_description = outputs[0]
    player.class_name = class_name
    player.race_name = race_name
    player.background_lore = background_lore
    player.race_description = race_description
    player.class_description = class_description
    print(player)
    print("---------------------------")


def adventure_hook():
    llm = LLM()

    lore_file = 'test/context.txt'

    with open(lore_file, 'r') as f:
        lore = f.read()

    player_list = []

    for i in range(2):
        player_file = f'test/player{i}.txt'

        with open(player_file, 'r') as f:
            player = f.read()

        player_list.append(player)

    human_input = "\n\n".join(
        [f"PLAYER {i} START\n" + str(p) + f"\nPLAYER {i} END" for i, p in enumerate(player_list)])

    print(human_input)

    result = llm.invoke('adventure_hook', human_input, context=lore)

    print(result.content)


def time_estimation():
    llm = LLM()

    messages = [
        SystemMessage(llm.config['systems']['time_estimation']),
        HumanMessage("Go on a date")
    ]

    llm = llm.llm.with_structured_output(TimeEstimate)

    print(llm.invoke(messages))


if __name__ == '__main__':
    # adventure_hook()
    # user_design(override=False)
    time_estimation()
