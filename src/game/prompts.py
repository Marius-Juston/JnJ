from game.advanced_message import AdvancedMessage


# Example class for user prompting
class UserPrompt(AdvancedMessage):
    def __init__(self, content = None, embed = None, author_id=None, emojis = None):

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
        if emojis is None:
            emojis =['✅', '❌']
        super().__init__(content=content,embed=embed, emojis=emojis, author_id=author_id, remove_buttons_on_finished = False)

        self.made_choice = False
        self.choice = None

    def finished(self):
        return self.made_choice

    async def callback(self, interaction, emoji):
        print(interaction, emoji)

        self.made_choice = True

        self.choice =  self.emojis.index(emoji)

        # await interaction.response.send_message('I selected ' + emoji)

        return True
