import discord
user_happy = False

class Adventure:
    def __init__(self, theme, lore):
        super().__init__()

        self.theme = theme
        self.lore = lore

    async def adventure_start(self,ctx):
        #TODO :  add the player list 
        embed=discord.Embed(title="New Adventure", description="This is an embed that will show how to build an embed and the different components", color=0x109319)
        embed.add_field(name="Theme", value=self.theme, inline=False)
        embed.add_field(name="Lore", value=self.lore, inline=True)
        embed.add_field(name="Player list", value=[], inline=True)
        embed.set_footer(text="Please use /Join_Adventure to join current adventure and type /begin adventure")

    def generate_lore(self):
        # TODO : FUTURE WILL BE DONE USING LLM

        return "The pie is a lie"

    async def process_lore(self, interaction: discord.Interaction):
        # TODO : GENERATE LORE HERE IF IT DOES NOT EXIST AND ASK USER IF THE CURRENT LORE IS GOOD OR NOT

        if self.lore is None:
            self.lore = self.generate_lore()
        else:
            user_happy = Ture
        
        while not user_happy:
            
            self.generate_lore



        pass
