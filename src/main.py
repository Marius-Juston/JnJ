from typing import Any, Optional

import discord
from discord import app_commands, Intents, InteractionResponse, Embed
from dotenv import dotenv_values

from game.adventure import Adventure
from game.discord.prompts import CharacterDetails
from game.player import Player


class MyClient(discord.Client):
    def __init__(self, *, intents: Intents, **options: Any):
        super().__init__(intents=intents, **options)

        self.synced = False

        self.tree = app_commands.CommandTree(self)

        self.start_adventure = self.tree.command(name='setup_adventure', description="Starts a new DnD story!")(
            self.start_adventure)
        self.add_user_to_adventure = self.tree.command(name='join', description="Adds user to the current adventure!")(
            self.add_user_to_adventure)

        self.flesh_out_character = self.tree.command(name='add_details',
                                                     description="Add aditional information for the character before adventure begins.")(
            self.flesh_out_character)

        self.clear_messages = self.tree.command(name='clear_messages', description="Clear this bot's messages")(
            self.clear_messages)

        self.start_ = self.tree.command(name='start',
                                        description="Closes the entry for new characters and starts the actual story adventure!")(
            self.start_)

        self.do_action = self.tree.command(name='perform',
                                           description="Perform whatever the current action the user wants to do for the current turn.")(
            self.do_action)

        self.terminate = self.tree.command(name='terminate',
                                           description="Finishes the current adventure process.")(
            self.terminate)

        self.adventures = dict()

    async def terminate(self, interaction: discord.Interaction):
        """
        Terminates the current adventure
        :return:
        """

        response: InteractionResponse = interaction.response

        if interaction.guild_id in self.adventures:
            await response.defer(thinking=False)

            adventure = self.adventures[interaction.guild_id]

            adventure.terminate()

            print("Set termination key")

            del self.adventures[interaction.guild_id]

            await interaction.edit_original_response(content="Adventure terminated")
        else:
            await response.send_message("No adventure to terminate")

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

    # async def on_message(self, message: discord.Message):
    #     print(f'Message from {message.author}: {message.content}')

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
            response: InteractionResponse = interaction.response

            await response.send_message(
                "Another adventure has already been started for this server. Currently only 1 can be run at the same time")
        else:
            new_adventure = Adventure(theme, lore)
            self.adventures[interaction.guild_id] = new_adventure

            await new_adventure.process_lore(interaction)

    async def add_user_to_adventure(self, interaction: discord.Interaction):
        """
        Join the DnD adventure
        :param interaction:
        :return:
        """
        if interaction.guild_id in self.adventures:
            adventure = self.adventures[interaction.guild_id]

            if adventure.has_player(interaction):
                await interaction.response.send_message(
                    f"You have already joined the adventure to customize character details do /{self.flesh_out_character.name}.")
            else:
                adventure.add_user(interaction.user)

                await interaction.response.send_message(
                    f"You have joined the adventure (to customize character details do /{self.flesh_out_character.name}, otherwise it will automatically generated)")
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

        if not adventure.has_player(interaction):
            adventure.add_user(interaction.user)

        user: Player = adventure.player_list[interaction.user.id]

        modal = CharacterDetails(user)

        await response.send_modal(modal)

    async def start_(self, interaction: discord.Interaction):

        response: InteractionResponse = interaction.response

        if interaction.guild_id not in self.adventures:
            await response.send_message("There are no adventures currently running")
            return

        adventure: Adventure = self.adventures[interaction.guild_id]

        if not adventure.ready:
            await response.send_message(
                f"The adventure is not ready yet, please complete the /{self.start_adventure.name} command!")
            return

        if not adventure.has_player(interaction):
            await response.send_message(
                "The member trying to start the adventure has not yet joined the adventure, please do "
                f"/{self.add_user_to_adventure.name} or /{self.flesh_out_character.name} to be added.")
            return

        if not adventure.started:
            await response.send_message(
                f"The adventure is has already been started, please perform an action using the /{self.do_action.name} command!")
            return

        await response.send_message(
            content=f"Let the adventure begin! Please have all the players call the /{self.do_action.name} command")

        await adventure.start_adventure(interaction)

    async def do_action(self, interaction: discord.Interaction, action: str):

        response: InteractionResponse = interaction.response

        if interaction.guild_id not in self.adventures:
            await response.send_message("There are no adventures currently running")
            return

        adventure: Adventure = self.adventures[interaction.guild_id]

        if not adventure.ready:
            await response.send_message(
                f"The adventure is not ready yet, please complete the /{self.start_adventure.name} command!")
            return

        if not adventure.has_player(interaction):
            if adventure.started:
                await response.send_message(
                    "The adventure has already started you will be unable to join the already started adventure.")
                return
            else:
                await response.send_message(
                    "The member trying to start the adventure has not yet joined the adventure, please do "
                    f"/{self.add_user_to_adventure.name} or /{self.flesh_out_character.name} to be added.")
                return

        if adventure.player_has_responded(interaction.user):
            await response.send_message(
                "The member has already responded to the current turn, once submitted you can no longer edit your responses!.")
            return

        embed = Embed(title=f"{adventure.get_player(interaction).character_name}'s Action")
        embed.add_field(name="Turn", value=str(adventure.turn_count))
        embed.add_field(name="Action", value=action, inline=False)

        await interaction.response.send_message(embed=embed)

        await adventure.add_user_response(interaction.user, action)


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
