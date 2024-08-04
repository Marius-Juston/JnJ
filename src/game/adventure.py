import discord

class Adventure:
    def __init__(self, theme, lore):
        super().__init__()

        self.theme = theme
        self.lore = lore

    async def adventure_announcement(self,ctx):
        #TODO :  add the player list 
        embed=discord.Embed(title="New Adventure", description="This is an embed that will show how to build an embed and the different components", color=0x109319)
        embed.add_field(name="Theme", value=self.theme, inline=False)
        embed.add_field(name="Lore", value=self.lore, inline=Flase)
        embed.add_field(name="Player list", value=[], inline=Flase)
        embed.set_footer(text="Please use /Join_Adventure to join current adventure and type /begin adventure")

    def generate_lore(self):
        # TODO : FUTURE WILL BE DONE USING LLM

        return "The pie is a lie"

    async def process_lore(self, interaction: discord.Interaction):
        # TODO : GENERATE LORE HERE IF IT DOES NOT EXIST AND ASK USER IF THE CURRENT LORE IS GOOD OR NOT
        user_happy = False
        if self.lore is None:
            print("No lore input")
            user_happy = False
        else:
            user_happy = True

        if user_happy = False:
            self.lore = self.generate_lore()
            print("New lore generated")
        else:
            print("Prompt user")
            # TODO : ask for user if this is a good lore
            user_happy = True
            



        pass
