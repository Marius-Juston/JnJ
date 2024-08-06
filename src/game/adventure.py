import discord
from game.prompts import UserPrompt
import asyncio

class Adventure:
    def __init__(self, theme, lore):
        super().__init__()

        self.theme = theme
        self.lore = lore
        print("strarting adventure")

    def generate_lore(self):
        # TODO : FUTURE WILL BE DONE USING LLM
        print("generate_lore ran")
        
        return "The pie is a lie"

    async def process_lore(self, interaction: discord.Interaction):
        print("process_lore running")

        if self.lore is None:
            print("no lore input")
            await interaction.response.defer(thinking= True)
            self.embed_lore = self.generate_lore()
            await asyncio.sleep(1) # TODO: remove when add generate_lore
            msg = await interaction.original_response()

            embed = self.adventure_announcement()
            await msg.edit(embed=embed)

            interaction.response.send_message(content= "Are you hapy with the current generated lore?")

        else:
            print("there is lore")
            self.embed_lore = self.lore
            adventure_message = self.adventure_announcement()
            await interaction.response.send_message(embed = adventure_message)
        
    def adventure_announcement(self):
        print("adventure_announcement running")
        embed_title = "New Adventure"
        # TODO :  add the player list
        embed = discord.Embed(title=embed_title, description="This is an embed that will show how to build an embed and the different components", color=0x109319)
        embed.add_field(name="Theme", value=self.theme, inline=False)
        embed.add_field(name="Lore", value=self.embed_lore, inline=False)
        embed.set_footer(text="Please use /Join_Adventure to join current adventure and type /begin_adventure when all players are ready ready")
        return embed
