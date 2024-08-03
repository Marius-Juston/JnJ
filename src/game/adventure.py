import discord


class Adventure:
    def __init__(self, theme, lore):
        super().__init__()

        self.theme = theme
        self.lore = lore

    def generate_lore(self):
        # FUTURE WILL BE DONE USING LLM

        return "The pie is a lie"

    def process_lore(self, interaction: discord.Interaction):
        # GENERATE LORE HERE IF IT DOES NOT EXIST AND ASK USER IF THE CURRENT LORE IS GOOD OR NOT

        if self.lore is None:
            self.lore = self.generate_lore()

        user_happy = False
        while not user_happy:
            pass

        pass
