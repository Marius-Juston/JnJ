from enum import Enum
from typing import Union, Any

import discord
from discord import Embed
from langchain_core.tools import tool
from pydantic import ValidationError

from game.llm import LLM, parse_tool_call


@tool
def player_(class_name: str, race_name: str, background_lore: str, race_description: str,
            class_description: str) -> Any:
    """This function is meant to collect the player information for the Dungeon and Dragon game.

    Args:
        class_name: (str) The DnD class of the character
        race_name: (str) The DnD race of the character.
        background_lore: (str) The detailed and comprehensive background lore of the character. 4096 characters or less
        race_description: (str) A detailed and comprehensive of the race of the character, key characteristics of that race and some description of the look of the race. 1024 characters or less
        class_description: (str) A detailed and comprehensive class description that explains what the class is about, and it's focus for of the character. 1024 characters or less
    """
    return class_name, race_name, background_lore, race_description, class_description


class Stats(Enum):
    STRENGTH = 0,
    DEXTERITY = 1,
    CONSTITUTION = 2,
    INTELLIGENCE = 3,
    WISDOM = 4,
    CHARISMA = 5,


class Player:
    def __init__(self, discord_user: Union[discord.User, discord.Member]):
        self.discord_user = discord_user

        self.stats = dict()

        for stat in Stats:
            self.stats[stat.name] = 0

        self.level = 0
        self.max_hp = 100
        self.current_hp = self.max_hp

        self.character_name = discord_user.display_name
        self.class_name = None
        self.race_name = None
        self.background_lore = None

        self.class_description = None
        self.race_description = None

    async def setup_stats(self, interaction: discord.Interaction):
        print(self.stats)

        embed = discord.Embed(title='Player stats',
                              description=f"This is user {self.discord_user.name}'s user stat allocation")

        await interaction.response.send(embed=embed)

    def __repr__(self) -> str:
        player = f"""
Character Name: {self.character_name if self.character_name else ''}
Character Background Lore: {self.background_lore if self.background_lore else ''}
Class Name: {self.class_name if self.class_name else ''}
Race Name: {self.race_name if self.race_name else ''}
Class Description: {self.class_description if self.class_description else ''}
Race Description: {self.race_description if self.race_description else ''}
                """.strip()
        return player

    def generate_embed(self):
        embed = Embed(title=self.character_name, description=self.background_lore)

        embed.add_field(name=f"Class: {self.class_name}", value=self.class_description, inline=True)
        embed.add_field(name=f"Race: {self.race_name}", value=self.race_description, inline=True)

        return embed

    def has_missing_info(self):
        return not (
                    self.character_name and self.race_name and self.background_lore and self.class_name and self.race_description and self.class_description)


async def generate_character(llm: LLM, player: Player, lore: str):
    character_sheet = str(player)

    result = await llm.ainvoke('character_creation', character_sheet, context=lore, tools=[player_], tool_choice='player_')

    if len(result.tool_calls) == 0:
        print("ERROR WITH TOOL CHOICE NOT WORKING!!")
        return

    try:
        outputs = parse_tool_call(result, player_)
    except ValidationError as e:
        print("THE NEURAL NETWORK DID NOT OUTPUT ALL THE PLAYER OUTPUTS!!!!")
        return

    class_name, race_name, background_lore, race_description, class_description = outputs[0]

    print(result)
    print("Character Details", result.tool_calls)

    if  len(race_name) <= 256:
        player.race_name = race_name
    else:
        print("race_name too large")

    if len(class_name) <= 256:
        player.class_name = class_name
    else:
        print("class_name too large")

    if  len(background_lore) <= 4096:
        player.background_lore = background_lore
    else:
        print("background_lore too large")

    if  len(race_description) <= 1024:
        player.race_description = race_description
    else:
        print("race_description too large")

    if  len(class_description) <= 1024:
        player.class_description = class_description
    else:
        print("class_description too large")


if __name__ == '__main__':
    class Temp:
        def __init__(self):
            self.display_name = "Marius"


    player = Player(Temp())

    print(str(player))
