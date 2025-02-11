import discord.ui
from discord import Interaction, InteractionResponse

from game.llm.llm import LLM
from game.messages.advanced_message import AdvancedMessage
from game.player import Player, generate_character


# Example class for user prompting
class UserPrompt(AdvancedMessage):
    def __init__(self, content=None, embed=None, author_id=None, emojis=None):
        """
        Example:
            advanced = UserPrompt(author_id=interaction.user.id)

            # await advanced.send(interaction)
            await advanced.send(interaction.response)

            print("Waiting")
            await advanced.wait_till_finished()
            print("Finished wating")

        :param author_id:
        """
        if emojis is None:
            emojis = ['✅', '❌']
        super().__init__(content=content, embed=embed, emojis=emojis, author_id=author_id,
                         remove_buttons_on_finished=False)

        self.made_choice = False
        self.choice = None

    def finished(self):
        return self.made_choice

    async def callback(self, interaction: Interaction, emoji: str):
        print(interaction, emoji)

        self.made_choice = True

        self.choice = self.emojis.index(emoji)

        return True


class CharacterDetails(discord.ui.Modal):
    def __init__(self, user: Player, adventure_lore):
        super().__init__(title='Character details')

        self.adventure_lore = adventure_lore
        self.user = user

        self.name_input = discord.ui.TextInput(label="Name", placeholder="Bob", default=user.character_name,
                                               style=discord.TextStyle.short, required=True)
        self.race_input = discord.ui.TextInput(label="Race", placeholder="Human", default=user.race_name,
                                               style=discord.TextStyle.short, required=False)
        self.class_input = discord.ui.TextInput(label="Class", placeholder="Fighter", default=user.class_name,
                                                style=discord.TextStyle.short, required=False)
        self.background_input = discord.ui.TextInput(label="Background", placeholder="Background",
                                                     default=user.background_lore,
                                                     style=discord.TextStyle.paragraph, required=False)

        self.add_item(self.name_input)
        self.add_item(self.class_input)
        self.add_item(self.race_input)
        self.add_item(self.background_input)

    async def on_submit(self, interaction: discord.Interaction):
        self.user.character_name = self.name_input.value

        if self.class_input.value != self.user.class_name:
            self.user.class_name = self.class_input.value
            self.user.class_description = None

        if self.race_input.value != self.user.race_name:
            self.user.race_name = self.race_input.value
            self.user.race_description = None

        self.user.background_lore = self.background_input.value

        response: InteractionResponse = interaction.response
        await response.defer(thinking=True)

        while self.user.has_missing_info():
            await generate_character(LLM(), self.user, self.adventure_lore)

        embed = self.user.generate_embed()

        await interaction.edit_original_response(embed=embed)
