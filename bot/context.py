from typing import Any, Dict, Optional

class MessageContext:
    def __init__(self, bot: Any, data: Dict[str, Any]):
        self.bot = bot
        self._data = data

        self.message_id: str = data.get("id")
        self.channel_id: str = data.get("channel_id")
        self.guild_id: Optional[str] = data.get("guild_id")

        self.content: str = data.get("content", "")
        self.author_id: str = data.get("author", {}).get("id")
        self.username: str = data.get("author", {}).get("username")

        self.member_data: Optional[Dict[str, Any]] = data.get("member")

    async def send(self, content: str, **kwargs):
        pass