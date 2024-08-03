import discord
from dotenv import dotenv_values


class MyClient(discord.Client):
    async def on_ready(self):
        print(f'Logged on as {self.user}!')

    async def on_message(self, message):
        print(f'Message from {message.author}: {message.content}')


if __name__ == '__main__':
    config = dotenv_values(".env")

    print(config)

    intents = discord.Intents.default()
    intents.message_content = True

    client = MyClient(intents=intents)
    client.run(config['BOT_TOKEN'])
