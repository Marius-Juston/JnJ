from typing import Union

from discord import InteractionResponse, TextChannel


async def send(location: Union[InteractionResponse, TextChannel], *args, **kwargs):
    if isinstance(location, TextChannel):
        return await location.send(*args, **kwargs)
    else:
        return await location.send_message(*args, **kwargs)
