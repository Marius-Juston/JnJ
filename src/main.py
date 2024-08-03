from typing import Any, Optional, Literal

import discord
from discord import app_commands, Intents
from dotenv import dotenv_values


class MyClient(discord.Client):
    def __init__(self, *, intents: Intents, **options: Any):
        super().__init__(intents=intents, **options)

        self.synced = False

        self.tree = app_commands.CommandTree(self)

        self.running = self.tree.command(name='running', description="running faster")(self.running)

    async def on_ready(self):
        print(f'Logged on as {self.user}!')

        print(self.tree)

        await self.wait_until_ready()
        if not self.synced:
            print("Syncing tree")
            await self.tree.sync()
            print("Synced tree")
            self.synced = True

    async def on_message(self, message):
        print(f'Message from {message.author}: {message.content}')

    async def running(self, interaction: discord.Interaction, name: str, infor: int,
                      superman: Optional[Literal['help', 'cheese']]):
        print("Hello", interaction, name)


if __name__ == '__main__':
    config = dotenv_values(".env")

    print(config)

    intents = discord.Intents.default()
    intents.message_content = True

    client = MyClient(intents=intents)
    client.run(config['BOT_TOKEN'])
