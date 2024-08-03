from typing import Any, Optional, Literal

import discord
from discord import app_commands, Intents
from dotenv import dotenv_values

from game.adventure import Adventure


class MyClient(discord.Client):
    def __init__(self, *, intents: Intents, **options: Any):
        super().__init__(intents=intents, **options)

        self.synced = False

        self.tree = app_commands.CommandTree(self)

        self.start_adventure = self.tree.command(name='start_adventure', description="Starts a new DnD story!")(
            self.start_adventure)

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
        new_adventure = Adventure(theme, lore)

        new_adventure.process_lore(interaction)


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
