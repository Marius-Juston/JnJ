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

        self.character_name = None
        self.class_name = None
        self.race_name = None
        self.background_lore = None

    def setup_player(self, name, class_name, race_name):
        pass

    async def setup_stats(self, interaction: discord.Interaction):
        print(self.stats)

        embed = discord.Embed(title='Player stats',
                              description=f"This is user {self.discord_user.name}'s user stat allocation")

        await interaction.response.send(embed=embed)

    async def Join_Adventure():
        player_list_alive = []
        player_list_alive.append(author_id)


if __name__ == '__main__':
    player = Player(None)
