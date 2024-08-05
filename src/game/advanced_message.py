from abc import ABC, abstractmethod
from functools import partial
from typing import Union, List, Optional, Callable, Any

from discord import InteractionResponse, TextChannel, ButtonStyle, Interaction
from discord.ui import View, Button


class MessageHandler:
    def __init__(self):
        self.messages = []

    def callback(self, data):
        for message in self.messages:
            finished = message(data)

            if finished:
                self.messages.remove(message)


class AdvancedMessage(ABC):

    def __init__(self, embed=None, content=None, emojis=None, author_id=None):
        self.emojis = emojis
        self.embed = embed
        self.content = content

        # Check if any info is expected to be sent for message
        if not (self.content or self.embed):
            self.content = '_ _'  # create message with empty text

        self.sent_message = None

        if self.emojis:
            self.view = EmojiSelection(emojis, author_id=author_id, callback_handler=self.callback)
        else:
            self.view = None

    @abstractmethod
    async def callback(self, interaction, emoji):
        raise NotImplementedError()

    def is_sent(self):
        return self.sent_message is not None

    async def send(self, location: Union[InteractionResponse, TextChannel]):
        if isinstance(location, InteractionResponse):
            self.sent_message = await location.send_message(content=self.content, embed=self.embed, view=self.view)
        else:
            self.sent_message = await location.send(content=self.content, embed=self.embed, view=self.view)


class EmojiSelection(View):
    def __init__(self, emojis: List[str], author_id: Optional[int] = None,
                 callback_handler: Optional[Callable[[str, Union[InteractionResponse, TextChannel], ], Any]] = None):
        super().__init__()

        self.author_id = author_id
        self.emojis = emojis

        for emoji in self.emojis:
            button = Button(style=ButtonStyle.blurple, emoji=emoji)

            if callback_handler:
                button.callback = partial(callback_handler, emoji=emoji)

            self.add_item(button)

    async def interaction_check(self, interaction: Interaction, /) -> bool:
        print(interaction.user.id, self.author_id)
        return not self.author_id or interaction.user.id == self.author_id
