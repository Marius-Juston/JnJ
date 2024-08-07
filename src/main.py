from typing import Any, Optional

import discord
from discord import app_commands, Intents, InteractionResponse, Embed
from discord.ui import Modal
from dotenv import dotenv_values

from game.adventure import Adventure
from game.player import Player


class MyClient(discord.Client):
    def __init__(self, *, intents: Intents, **options: Any):
        super().__init__(intents=intents, **options)

        self.synced = False

        self.tree = app_commands.CommandTree(self)

        self.start_adventure = self.tree.command(name='start_adventure', description="Starts a new DnD story!")(
            self.start_adventure)
        self.add_user_to_adventure = self.tree.command(name='join', description="Adds user to the current adventure!")(
            self.add_user_to_adventure)

        self.flesh_out_character = self.tree.command(name='add_details',
                                                     description="Add aditional information for the character before adventure begins.")(
            self.flesh_out_character)

        self.clear_messages = self.tree.command(name='clear_messages', description="Clear this bot's messages")(
            self.clear_messages)

        self.adventures = dict()

    async def clear_messages(self, interaction: discord.Interaction):

        response: InteractionResponse = interaction.response
        await response.defer(thinking=True, ephemeral=True)

        deleted = await interaction.channel.purge(limit=100, check=lambda msg: msg.author == self.user)

        await interaction.edit_original_response(content=f'Deleted {len(deleted)} message(s)')

    async def on_ready(self):
        print(f'Logged on as {self.user}!')

        print(self.tree)

        await self.wait_until_ready()
        if not self.synced:
            print("Syncing tree")
            await self.tree.sync()
            print("Synced tree")
            self.synced = True

    async def on_message(self, message: discord.Message):
        print(f'Message from {message.author}: {message.content}')

    async def start_adventure(self, interaction: discord.Interaction, theme: str,
                              lore: Optional[str]):
        """
        Starts the DnD adventure
        :param interaction:
        :param theme: The adventure theme
        :param lore: The optional starting lore for the adventure
        :return:
        """

        if interaction.guild_id in self.adventures:
            await self.adventure_started_warning(interaction)
        else:
            new_adventure = Adventure(theme, lore)
            self.adventures[interaction.guild_id] = new_adventure

            await new_adventure.process_lore(interaction)

    async def adventure_started_warning(self, interaction: discord.Interaction):
        response: InteractionResponse = interaction.response

        await response.send_message(
            "Another adventure has already been started for this server. Currently only 1 can be run at the same time")

    async def add_user_to_adventure(self, interaction: discord.Interaction):
        """
        Join the DnD adventure
        :param interaction:
        :return:
        """
        if interaction.guild_id in self.adventures:
            adventure = self.adventures[interaction.guild_id]
            adventure.add_user(interaction.user)
            await interaction.response.send_message("You have joined the adventure", ephemeral=Ture)
        else:
            await interaction.response.send_message("There is no adventure currently running")

    async def flesh_out_character(self, interaction: discord.Interaction):
        # TODO Cleanup this function to be more appropriately written

        response: InteractionResponse = interaction.response

        if interaction.guild_id not in self.adventures:
            await response.send_message("There are no adventures currently running")
            return

        adventure: Adventure = self.adventures[interaction.guild_id]

        if adventure.started:
            await response.send_message("Cannot add details to game that is already running")
            return

        if interaction.user.id not in adventure.player_list:
            adventure.add_user(interaction.user)

        user: Player = adventure.player_list[interaction.user.id]

        modal = Modal(title="Character Information")

        name_input = discord.ui.TextInput(label="Name", placeholder="Bob", default=interaction.user.name,
                                          style=discord.TextStyle.short, required=True)
        race_input = discord.ui.TextInput(label="Race", placeholder="Human", default="Human",
                                          style=discord.TextStyle.short, required=False)
        class_input = discord.ui.TextInput(label="Class", placeholder="Fighter", default="Fighter",
                                           style=discord.TextStyle.short, required=False)
        background_input = discord.ui.TextInput(label="Background", placeholder="Background",
                                                style=discord.TextStyle.paragraph, required=False)

        modal.add_item(name_input)
        modal.add_item(class_input)
        modal.add_item(race_input)
        modal.add_item(background_input)

        async def on_submit(interaction: discord.Interaction):
            user.character_name = name_input.value
            user.class_name = class_input.value
            user.race_name = race_input.value
            user.background_lore = background_input.value

            embed = Embed(title="Submitted Character details")

            embed.add_field(name="Character Name", value=user.character_name)
            embed.add_field(name="Class Name", value=user.class_name)
            embed.add_field(name="Race Name", value=user.race_name)
            embed.add_field(name="Background", value=user.background_lore, inline=False)

            await interaction.response.send_message(embed=embed)

        modal.on_submit = on_submit

        await response.send_modal(modal)


if __name__ == '__main__':
    #  Loads the secrets configuration data from the .env file
    config = dotenv_values(".env")

    # Prints it out for bebugging sake
    print(config)

    # Intent of that the client is planning to use
    intents = discord.Intents.default()
    intents.message_content = True

    # Crease the client
    client = MyClient(intents=intents)

    # Start the client using the TOKEN stored in the .env
    client.run(config['BOT_TOKEN'])
