import threading
from random import shuffle
from typing import Union, Optional, List, Tuple

import discord
from discord import Interaction, TextChannel, Message

from game.messages.prompts import UserPrompt
from game.llm import LLM
from game.player import Player


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

        self._terminate = threading.Event()

        self.llm = LLM()

    def has_player(self, interaction: Interaction) -> bool:
        return interaction.user.id in self.player_list

    def get_player(self, interaction: Interaction) -> Player:
        return self.player_list[interaction.user.id]

    async def generate_lore(self, user: Optional[UserPrompt] = None) -> Tuple[str, List[Message]]:
        print("generate_lore ran")

        messages = []
        lore = ''

        async for message_chunk in self.llm.astream('lore', self.theme, self._terminate):
            if not message_chunk or (user and user.is_finished and user.choice == 1):
                return lore, messages

            message = await self.channel.send(message_chunk.strip())

            lore += message_chunk

            messages.append(message)

        return lore, messages

    async def delete_messages(self, messages: List[Message]) -> None:
        for message in messages:
            await message.delete()

    async def process_lore(self, interaction: discord.Interaction) -> None:
        self.channel = interaction.channel

        print("process_lore running")
        await interaction.response.defer(thinking=True)

        if self.lore is None:
            embed_lore, messages = await self.generate_lore()
        else:
            embed_lore = self.lore
            messages = []

        # sends the embed message
        msg = await interaction.original_response()
        embed = self.adventure_announcement(self.lore is not None)
        await msg.edit(embed=embed)

        opt = UserPrompt(content="Are you hapy with the current generated lore?")
        await opt.send(interaction.channel)

        await opt.wait_till_finished(self._terminate)
        selection = opt.choice

        while not self._terminate.is_set() and selection != 0:
            self.lore = None
            opt.reset()

            self.lore = None
            print("picked false")

            await self.delete_messages(messages)
            await msg.edit(embed=None, content="Generating new lore, Thank you for your patience")

            embed_lore, messages = await self.generate_lore(opt)
            embed = self.adventure_announcement(self.lore is not None)

            await msg.edit(embed=embed, content=None)

            await opt.wait_till_finished(self._terminate)

            selection = opt.choice

        self.lore = embed_lore

        self.ready = True

        await opt.delete()

    def adventure_announcement(self, show_lore=True) -> discord.Embed:
        embed_title = "New Adventure"
        embed = discord.Embed(title=embed_title,
                              description="This is an embed that will show how to build an embed and the different components",
                              color=0x109319)
        embed.add_field(name="Theme", value=self.theme, inline=False)

        if show_lore:
            embed.add_field(name="Lore", value=self.lore, inline=False)

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
            if not self._terminate.is_set():
                break

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

    def terminate(self):
        self._terminate.set()

    async def generate_character_details(self, interaction: discord.Interaction):
        response: InteractionResponse = interaction.response

        await response.defer(thinking=True)

        player = self.get_player(interaction)

        while player.has_missing_info():
            await generate_character(self.llm, player, self.lore)

        await interaction.edit_original_response(embed=player.generate_embed())
