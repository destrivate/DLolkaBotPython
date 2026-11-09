from __future__ import annotations

import asyncio
import json
import types
from typing import TYPE_CHECKING

import requests
import websockets

from .context import MessageContext
from .cog import Cog

class Bot:
    def __init__(self,TOKEN: str):
        self.event = None
        self.TOKEN = TOKEN
        self.GATEWAY_URL = "wss://lolka.app/ws/bot?v=10&encoding=json"
        self.BOT_ID = ""

        self.COGS = []
        self.COMMANDS = {}

    def reg_cog(self,cog: Cog):
        self.COGS.append(cog)   

    async def send_message(self,channel_id, text_content):
        url = f"https://lolka.app/api/bot/v10/channels/{channel_id}/messages"

        headers = {
            "Authorization": f"Bot {self.TOKEN}",
            "Content-Type": "application/json"
        }

        payload = {"content": text_content}

        def post_request():
            return requests.post(url, json=payload, headers=headers)

        await asyncio.to_thread(post_request)


    async def _bot_ws(self):
        async with websockets.connect(self.GATEWAY_URL) as websocket:
            hello_event = await websocket.recv()
            hello_data = json.loads(hello_event)
            heartbeat_interval = hello_data['d']['heartbeat_interval'] / 1000
            identify_payload = {
                "op": 2,
                "d": {
                    "token": self.TOKEN,
                    "intents": 33280,
                    "capabilities": 16383,
                    "properties": {
                        "os": "linux",
                        "browser": "linux",
                        "device": "linux"
                    },
                    "presence": {
                        "status": "online",
                        "afk": False
                    }
                }
            }
            await websocket.send(json.dumps(identify_payload))

            async def keep_alive():
                while True:
                    await asyncio.sleep(heartbeat_interval)
                    heartbeat_payload = {"op": 1, "d": None}
                    await websocket.send(json.dumps(heartbeat_payload))

            asyncio.create_task(keep_alive())
            try:
                async for message in websocket:
                    event = json.loads(message)
                    print(f"[<-] Событие (Opcode {event.get('op')}): {event.get('t')}")
                    if event.get('t') == "READY":
                        self.BOT_ID = event.get('d', {}).get('user', {}).get('id')
                    if event.get('t') == 'MESSAGE_CREATE':
                        msg = event.get('d', {})
                        if self.BOT_ID == msg.get('author', {}).get('id'):
                            continue
                        for c in self.COGS:
                            context = MessageContext(c.bot,msg)
                            await c.check_command(context)

                    await self.event(event)

            except websockets.ConnectionClosed as e:
                print(f"{e}")


    async def loop(self,event: types.FunctionType):
        self.event = event
        await self._bot_ws()
