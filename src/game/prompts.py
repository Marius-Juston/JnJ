from game.advanced_message import AdvancedMessage


# Example class for user prompting
class UserPrompt(AdvancedMessage):
    def __init__(self, embed = None, author_id=None):
        """
        Example:
            advanced = UserPrompt(author_id=interaction.user.id)

            # await advanced.send(interaction.channel)
            await advanced.send(interaction.response)

            print("Waiting")
            await advanced.wait_till_finished()
            print("Finished wating")

        :param author_id:
        """
        content = None
        if embed is None:
            content = "are you happy?"
            
        super().__init__(content=content,embed=embed, emojis=['✅', '❌'], author_id=author_id)

        self.made_choice = False
        self.choice = None

    def finished(self):
        return self.made_choice

    async def callback(self, interaction, emoji):
        print(interaction, emoji)

        self.made_choice = True

        self.choice = '✅' == emoji

        await interaction.response.send_message('I selected ' + emoji)

        return True
