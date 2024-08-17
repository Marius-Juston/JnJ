from enum import Enum
from typing import Union, Any

import discord
from discord import Embed

from game.llm import LLM


def player_(class_name: str, race_name: str, background_lore: str) -> Any:
    """This function is meant to collect the player information for the Dungeon and Dragon game.

    Args:
        class_name: (str) The DnD class of the character
        race_name: (str) The DnD race of the character.
        background_lore: (str) The detailed and comprehensive background lore of the character.
    """
    return class_name, race_name, background_lore


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
                """.strip()
        return player

    def generate_embed(self):
        embed = Embed(title="Submitted Character details")

        embed.add_field(name="Character Name", value=self.character_name)
        embed.add_field(name="Class Name", value=self.class_name)
        embed.add_field(name="Race Name", value=self.race_name)
        embed.set_footer(text=self.background_lore)

        return embed

    def has_missing_info(self):
        return not (self.character_name and self.race_name and self.background_lore and self.class_name)


async def generate_character(llm: LLM, player: Player, lore: str):
    character_sheet = str(player)

    result = await llm.ainvoke('character_creation', character_sheet, context=lore, tools=[player_])

    if len(result.tool_calls) == 0:
        return

    character_details = result.tool_calls[0]['args']

    print(result)
    print("Character Details", result.tool_calls)

    player.race_name = character_details['race_name']
    player.class_name = character_details['class_name']
    player.background_lore = character_details['background_lore']


if __name__ == '__main__':
    class Temp:
        def __init__(self):
            self.display_name = "Marius"


    player = Player(Temp())

    print(str(player))
