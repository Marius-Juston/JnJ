import discord


class Adventure:
    def __init__(self, theme, lore):
        super().__init__()

        self.theme = theme
        self.lore = lore
        self.process_lore()

    def generate_lore(self):
        # TODO : FUTURE WILL BE DONE USING LLM
        print("generate_lore ran")
        return "The pie is a lie"

    async def process_lore(self, interaction: discord.Interaction):
        # TODO : GENERATE LORE HERE IF IT DOES NOT EXIST AND ASK USER IF THE CURRENT LORE IS GOOD OR NOT
        user_happy = False
        if self.lore is None:
            print("No lore input")
            user_happy = False
        else:
            user_happy = True

        if user_happy is False:
            self.lore = self.generate_lore()
            print("New lore generated")
            self.adventure_announcement()
            # TODO : prompt user if they like the lore
            self.user_choice = player_prompt()
            if user_choice is 0:
                self.lore = None
                self.process_lore()
            if user_choice is 1:
                user_happy = True
                return self.lore
        else:
            self.adventure_announcement(self.theme, self.lore)

        return self.lore

    async def adventure_announcement(self, ctx):
        # TODO :  add the player list
        embed = discord.Embed(title="New Adventure", description="This is an embed that will show how to build an embed and the different components", color=0x109319)
        embed.add_field(name="Theme", value=self.theme, inline=False)
        embed.add_field(name="Lore", value=self.lore, inline=False)
        embed.add_field(name="Player list", value=[], inline=False)
        embed.set_footer(text="Please use /Join_Adventure to join current adventure and type /begin_adventure when all players are ready ready")
        AdvancedMessage()
        pass
