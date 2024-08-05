import asyncio
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


class AdvancedMessage(ABC):
    view: Optional[EmojiSelection]

    def __init__(self, embed=None, content=None, emojis=None, author_id=None, remove_buttons_on_finished=True):
        self.emojis = emojis
        self.embed = embed
        self.content = content
        self.remove_buttons_on_finished = remove_buttons_on_finished

        self.is_finished = False

        # Check if any info is expected to be sent for message
        if not (self.content or self.embed):
            self.content = '_ _'  # create message with empty text

        self.sent_message = None

        if self.emojis:
            self.view = EmojiSelection(emojis, author_id=author_id, callback_handler=self._callback)
        else:
            self.view = None

    async def wait_till_finished(self):
        while not self.is_finished:
            await asyncio.sleep(.1)

    async def _callback(self, interaction: Interaction, emoji: str):
        self.is_finished = await self.callback(interaction, emoji)

        if self.is_finished and self.remove_buttons_on_finished:
            await interaction.message.edit(view=None)

    @abstractmethod
    async def callback(self, interaction: Interaction, emoji: str) -> bool:
        raise NotImplementedError()

    def is_sent(self):
        return self.sent_message is not None

    async def send(self, location: Union[InteractionResponse, TextChannel]):
        if isinstance(location, InteractionResponse):
            self.sent_message = await location.send_message(content=self.content, embed=self.embed, view=self.view)
        else:
            self.sent_message = await location.send(content=self.content, embed=self.embed, view=self.view)
