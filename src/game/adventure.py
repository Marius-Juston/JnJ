import asyncio

import discord

from game.prompts import UserPrompt


class Adventure:
    def __init__(self, theme, lore):
        super().__init__()

        self.theme = theme
        self.lore = lore
        print("strarting adventure")

    def generate_lore(self):
        # TODO : FUTURE WILL BE DONE USING LLM
        asyncio.sleep(1)
        print("generate_lore ran")

        return "The pie is a lie"

    async def process_lore(self, interaction: discord.Interaction):
        print("process_lore running")
        await interaction.response.defer(thinking=True)

        if self.lore is None:
            self.embed_lore = self.generate_lore()

        else:
            self.embed_lore = self.lore

        # sends the embed message
        msg = await interaction.original_response()
        embed = self.adventure_announcement()
        await msg.edit(embed=embed)

        opt = UserPrompt(content="Are you hapy with the current generated lore?")
        await opt.send(interaction.channel)
        await opt.wait_till_finished()
        selection = opt.choice

        while selection != 0:
            print("picked false")
            await msg.edit(embed=None, content="Generating new lore, Thank you for your patience")
            self.embed_lore = self.generate_lore()
            embed = self.adventure_announcement()
            await msg.edit(embed=embed, content=None)
            opt.reset()
            await opt.wait_till_finished()
            selection = opt.choice

        await opt.remove_buttons()

    def adventure_announcement(self):
        print("adventure_announcement running")
        embed_title = "New Adventure"
        # TODO :  add the player list
        embed = discord.Embed(title=embed_title,
                              description="This is an embed that will show how to build an embed and the different components",
                              color=0x109319)
        embed.add_field(name="Theme", value=self.theme, inline=False)
        embed.add_field(name="Lore", value=self.embed_lore, inline=False)
        embed.set_footer(
            text="Please use /Join_Adventure to join current adventure and type /begin_adventure when all players are ready ready")
        return embed
