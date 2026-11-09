from __future__ import annotations

from typing import TYPE_CHECKING

from .context import MessageContext

if TYPE_CHECKING:
    from .bot import Bot

class Cog:
    def __init__(self, bot: Bot):
        self.bot: Bot = bot

    def command(self,command: str):
        def decorator(func):
            self.bot.COMMANDS[command] = func
            return func
        return decorator

    async def check_command(self,message_context: MessageContext):
        func = self.bot.COMMANDS.get(message_context.content)
        if func:
            await func(message_context)
