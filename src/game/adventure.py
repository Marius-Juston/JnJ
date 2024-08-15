import asyncio
from random import shuffle
from typing import Union, Optional

import discord
from discord import Interaction, TextChannel

from game.player import Player
from game.discord.prompts import UserPrompt


class Adventure:
    def __init__(self, theme, lore):
        super().__init__()

        self.theme = theme
        self.lore = lore
        self.player_list = dict()
        self.started = False

        self.ready = False

        print("strarting adventure")

        self.channel: Optional[TextChannel] = None

        self.player_responses = dict()
        self.turn_count = 0

    def has_player(self, interaction: Interaction) -> bool:
        return interaction.user.id in self.player_list

    def get_player(self, interaction: Interaction) -> Player:
        return self.player_list[interaction.user.id]

    async def generate_lore(self) -> str:
        # TODO : FUTURE WILL BE DONE USING LLM
        print("generate_lore ran")
        await asyncio.sleep(1)

        return "The pie is a lie"

    async def process_lore(self, interaction: discord.Interaction) -> None:
        self.channel = interaction.channel

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

    def adventure_announcement(self) -> discord.Embed:
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

    def add_user(self, user: Union[discord.Member, discord.User]) -> None:
        new_user = Player(user)
        self.player_list[user.id] = new_user

    async def start_adventure(self, interaction: Interaction):
        pass

    def player_has_responded(self, user) -> bool:
        return user.id in self.player_responses

    def all_responded(self) -> bool:
        return len(self.player_responses) == len(self.player_list)

    def next_turn(self) -> None:
        self.turn_count += 1
        self.player_responses = dict()

    async def perform_actions(self) -> None:
        player_list = list(self.player_responses.keys())
        shuffle(player_list)

        for player in player_list:
            player = self.player_list[player]

            await self.perform_user_action(player)

        self.next_turn()

    async def perform_user_action(self, user: Player) -> None:
        await self.channel.send(content=f"Performing the action for {user.character_name}")

    async def world_turn(self) -> None:
        await self.channel.send(content="All the players have played it is now the WORLD's turn")

    async def add_user_response(self, user: Union[discord.Member, discord.User], content: str) -> None:
        self.player_responses[user.id] = content

        if self.all_responded():
            await self.perform_actions()

            await self.world_turn()
