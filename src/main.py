from typing import Any, Optional

import discord
from discord import app_commands, Intents, InteractionResponse
from discord.ui import Modal
from dotenv import dotenv_values

from game.adventure import Adventure


class MyClient(discord.Client):
    def __init__(self, *, intents: Intents, **options: Any):
        super().__init__(intents=intents, **options)

        self.synced = False

        self.tree = app_commands.CommandTree(self)

        self.start_adventure = self.tree.command(name='start_adventure', description="Starts a new DnD story!")(
            self.start_adventure)
        self.add_user_to_adventure = self.tree.command(name='join', description="Adds user to the current adventure!")(
            self.add_user_to_adventure)

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
        new_adventure = Adventure(theme, lore)

        if interaction.guild_id in self.adventures:
            await self.adventure_started_warning(interaction)
        else:
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
            # add author_id
            pass
        else:
            await interaction.response.send("There is no adventure currently running")

        pass

    async def flesh_out_character(self, interaction: discord.Interaction):
        modal = Modal(title="Character Information")

        class_input = discord.ui.TextInput(label="Class", placeholder="Human", default="Human",
                                           style=discord.TextStyle.short)
        race_input = discord.ui.TextInput(label="Race", placeholder="Human", default="Human",
                                          style=discord.TextStyle.short)


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
