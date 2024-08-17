import asyncio
import threading
from abc import ABC, abstractmethod
from functools import partial
from typing import Union, List, Optional, Callable, Any

from discord.errors import NotFound
from discord import InteractionResponse, TextChannel, ButtonStyle, Interaction, InteractionMessage, Message
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
    sent_message: Union[InteractionMessage, Message]

    def __init__(self, embed=None, content=None, view=None, emojis=None, author_id=None,
                 remove_buttons_on_finished=True,
                 auto_defer=True):
        self.auto_defer = auto_defer
        self.emojis = emojis
        self.embed = embed
        self.content = content
        self.remove_buttons_on_finished = remove_buttons_on_finished

        self.is_finished = False

        # Check if any info is expected to be sent for message
        if not (self.content or self.embed):
            self.content = '_ _'  # create message with empty text

        self.sent_message = None

        if view is None and self.emojis:
            self.view = EmojiSelection(emojis, author_id=author_id, callback_handler=self._callback)
        else:
            self.view = view

    async def wait_till_finished(self, early_termination: Optional[threading.Event] = None):
        while not early_termination.is_set() and not self.is_finished:
            await asyncio.sleep(.1)

    async def _callback(self, interaction: Interaction, emoji: str):
        self.is_finished = await self.callback(interaction, emoji)

        if self.is_finished and self.remove_buttons_on_finished:
            await self.remove_buttons()

        if self.auto_defer:
            response: InteractionResponse = interaction.response

            await response.defer()

    async def remove_buttons(self):
        self.view.stop()
        await self.sent_message.edit(view=None)

    def reset(self):
        self.is_finished = False

    async def delete(self):
        if self.is_sent():
            try:
                await self.sent_message.delete()
            except NotFound:
                pass

    @abstractmethod
    async def callback(self, interaction: Interaction, emoji: str) -> bool:
        raise NotImplementedError()

    def is_sent(self):
        return self.sent_message is not None

    async def send(self, location: Union[Interaction, TextChannel]):
        if isinstance(location, Interaction):
            response: InteractionResponse = location.response

            await response.send_message(content=self.content, embed=self.embed, view=self.view)

            self.sent_message = location.original_response()
        else:
            self.sent_message = await location.send(content=self.content, embed=self.embed, view=self.view)
