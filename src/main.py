from typing import Any, Optional

import discord
from discord import app_commands, Intents, InteractionResponse, Embed, Role, Webhook, AllowedMentions
from dotenv import dotenv_values

from game.adventure import Adventure
from game.messages.prompts import CharacterDetails
from game.player import Player


class MyClient(discord.Client):
    def __init__(self, *, intents: Intents, **options: Any):
        super().__init__(intents=intents, **options)

        self.synced = False

        self.tree = app_commands.CommandTree(self)

        self.setup_adventure = self.tree.command(name='setup_adventure', description="Starts a new DnD story!")(
            self.setup_adventure)

        self.join = self.tree.command(name='join', description="Adds user to the current adventure!")(
            self.join)

        self.clear_messages = self.tree.command(name='clear_messages', description="Clear this bot's messages")(
            self.clear_messages)

        self.start_ = self.tree.command(name='start',
                                        description="Closes the entry for new characters and starts the actual story adventure!")(
            self.start_)

        self.perform = self.tree.command(name='perform',
                                         description="Perform whatever the current action the user wants to do for the current turn.")(
            self.perform)

        self.add_random = self.tree.command(name='add_random',
                                            description="For testing purposes add a random user")(
            self.add_random)

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

            await adventure.terminate()

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

    async def setup_adventure(self, interaction: discord.Interaction, theme: str,
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
            new_adventure = Adventure(theme, lore, interaction.guild)
            await new_adventure.setup_roles()

            self.adventures[interaction.guild_id] = new_adventure

            await new_adventure.process_lore(interaction)

    async def join(self, interaction: discord.Interaction, add_details: bool = False):
        """
        Join the DnD adventure
        :param interaction:
        :param add_details: Boolean flag to enable modifying / setting the character details
        :return:
        """
        response: InteractionResponse = interaction.response

        if interaction.guild_id not in self.adventures:
            await response.send_message("There is no adventure currently running")
            return

        adventure = self.adventures[interaction.guild_id]

        if adventure.started:
            await response.send_message("Cannot join / add character details to game that is already running")
            return

        if not adventure.ready:
            await response.send_message(
                f"The adventure is not ready yet, please complete the /{self.setup_adventure.name} command!")
            return

        first_time = False

        change_details = add_details
        if adventure.has_player(interaction):
            change_details = True
        else:
            first_time = True
            await adventure.add_user(interaction.user)

        if change_details:
            user: Player = adventure.player_list[interaction.user.id]

            modal = CharacterDetails(user, adventure.lore)

            await response.send_modal(modal)
        else:
            await adventure.generate_character_details(interaction)

            followup: Webhook = interaction.followup

            await followup.send(
                content=f"You have joined the adventure (to customize character details do /{self.join.name} add_details: True)",
                ephemeral=True)

        if first_time:
            followup: Webhook = interaction.followup
            role: Role = adventure.role
            await followup.send(
                f"<@&{role.id}> {interaction.user.display_name} has joined the adventure!",
                allowed_mentions=AllowedMentions.all())

    async def add_random(self, interaction: discord.Interaction):
        """
        Join the DnD adventure
        :param interaction:
        :return:
        """
        response: InteractionResponse = interaction.response

        if interaction.guild_id not in self.adventures:
            await response.send_message("There is no adventure currently running")
            return

        adventure = self.adventures[interaction.guild_id]

        if adventure.started:
            await response.send_message("Cannot join / add character details to game that is already running")
            return

        if not adventure.ready:
            await response.send_message(
                f"The adventure is not ready yet, please complete the /{self.setup_adventure.name} command!")
            return

        member = None

        async for member_ in interaction.guild.fetch_members(limit=150):
            if not member_.bot and member_.id not in adventure.player_list:
                member = member_
                break

        if member is None:
            await response.send_message(
                f"No more players to add, they have been all added!")
            return

        await adventure.add_user(member)

        interaction.user = member

        await adventure.generate_character_details(interaction)

    async def start_(self, interaction: discord.Interaction):

        response: InteractionResponse = interaction.response

        if interaction.guild_id not in self.adventures:
            await response.send_message("There are no adventures currently running")
            return

        adventure: Adventure = self.adventures[interaction.guild_id]

        if not adventure.ready:
            await response.send_message(
                f"The adventure is not ready yet, please complete the /{self.setup_adventure.name} command!")
            return

        if not adventure.has_player(interaction):
            await response.send_message(
                "The member trying to start the adventure has not yet joined the adventure, please do "
                f"/{self.join.name} to be added.")
            return

        if adventure.started:
            await response.send_message(
                f"The adventure has already been started, please perform an action using the /{self.perform.name} command!")
            return

        await adventure.start_adventure(interaction)

    async def perform(self, interaction: discord.Interaction, action: str):

        response: InteractionResponse = interaction.response

        if interaction.guild_id not in self.adventures:
            await response.send_message("There are no adventures currently running")
            return

        adventure: Adventure = self.adventures[interaction.guild_id]

        if not adventure.ready:
            await response.send_message(
                f"The adventure is not ready yet, please complete the /{self.setup_adventure.name} command!")
            return

        if not adventure.has_player(interaction):
            if adventure.started:
                await response.send_message(
                    "The adventure has already started you will be unable to join the already started adventure.")
                return
            else:
                await response.send_message(
                    "The member trying to start the adventure has not yet joined the adventure, please do "
                    f"/{self.join.name} or /{self.add_details.name} to be added.")
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
    intents.members = True

    # Crease the client
    client = MyClient(intents=intents)

    # Start the client using the TOKEN stored in the .env
    client.run(config['BOT_TOKEN'])
