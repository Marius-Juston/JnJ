import os
from random import SystemRandom
from typing import Union

import discord
from discord import InteractionResponse, TextChannel

from game.util import send


class Dice:
    def __new__(cls):
        if not hasattr(cls, 'instance'):
            cls.instance = super(Dice, cls).__new__(cls)
        return cls.instance

    def __init__(self, gif_folder='assets/dice/gifs', max_dice=20):
        self.max_dice = max_dice
        if hasattr(self, 'gifs'):
            return

        self.gif_folder = gif_folder

        self.random = SystemRandom()

        self.cache = dict()

    def load_image(self, index):
        if index not in self.cache:

            file = discord.File(os.path.join(self.gif_folder, f"{index}.gif"), filename=f"{index}.gif")
            embed = discord.Embed(title="Dice roll")
            embed.set_image(url=f"attachment://{index}.gif")

            self.cache[index] = (file, embed)
        else:
            file, embed = self.cache[index]

        return file, embed

    def roll(self):
        return self.random.randint(1, self.max_dice)

    async def roll_dice(self, channel: Union[InteractionResponse, TextChannel], roll=None):
        random_selection = self.roll() if roll is None else roll

        file, embed = self.load_image(random_selection)

        await send(channel, file=file, embed=embed)

        return random_selection
