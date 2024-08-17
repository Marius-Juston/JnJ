from enum import Enum
from typing import Union

import discord


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
        self.class_name = "Fighter"
        self.race_name = "Human"
        self.background_lore = None

    async def setup_stats(self, interaction: discord.Interaction):
        print(self.stats)

        embed = discord.Embed(title='Player stats',
                              description=f"This is user {self.discord_user.name}'s user stat allocation")

        await interaction.response.send(embed=embed)

    def __repr__(self) -> str:
        player = f"""
Character Name: {self.character_name if self.character_name else ''} 
Class Name: {self.class_name if self.class_name else ''} 
Race Name: {self.race_name if self.race_name else ''} 
Character Background Lore: {self.background_lore if self.background_lore else ''} 
                """.strip()
        return player


if __name__ == '__main__':
    player = Player(None)
