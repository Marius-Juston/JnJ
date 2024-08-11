import asyncio
from typing import Union

import discord
from discord import Interaction

from game.player import Player
from game.prompts import UserPrompt


class Adventure:
    def __init__(self, theme, lore):
        super().__init__()

        self.theme = theme
        self.lore = lore
        self.player_list = dict()
        self.started = False

        self.ready = False

        print("strarting adventure")

    def has_player(self, interaction: Interaction):
        return interaction.user.id in self.player_list

    async def generate_lore(self):
        # TODO : FUTURE WILL BE DONE USING LLM
        print("generate_lore ran")
        await asyncio.sleep(1)

        return "The pie is a lie"

    async def process_lore(self, interaction: discord.Interaction):
        print("process_lore running")
        await interaction.response.defer(thinking=True)

        if self.lore is None:
            self.embed_lore = await self.generate_lore()

        else:
            self.embed_lore = self.lore

        # sends the embed message
        msg = await interaction.original_response()
        embed = self.adventure_announcement()
        await msg.edit(embed=embed)

        opt = UserPrompt(content="Are you hapy with the current generated lore?")
        await opt.send(interaction.channel)
        await opt.wait_till_finished()
        selection = opt.choice

        while selection != 0:
            print("picked false")
            await msg.edit(embed=None, content="Generating new lore, Thank you for your patience")
            self.embed_lore = await self.generate_lore()
            embed = self.adventure_announcement()
            await msg.edit(embed=embed, content=None)
            opt.reset()
            await opt.wait_till_finished()
            selection = opt.choice

        self.ready = True

        await opt.delete()

    def adventure_announcement(self):
        print("adventure_announcement running")
        embed_title = "New Adventure"
        embed = discord.Embed(title=embed_title,
                              description="This is an embed that will show how to build an embed and the different components",
                              color=0x109319)
        embed.add_field(name="Theme", value=self.theme, inline=False)
        embed.add_field(name="Lore", value=self.embed_lore, inline=False)
        embed.set_footer(
            text="Please use /join or /add_details to join current adventure and type /start when all players are ready ready")
        # TODO Not make /join and /add_details to be hard-coded
        return embed

    def add_user(self, user: Union[discord.Member, discord.User]):
        new_user = Player(user)
        self.player_list[user.id] = new_user

    async def start_adventure(self, interaction: Interaction):
        pass
