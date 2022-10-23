"""Utilities"""

import asyncio
from functools import wraps

from simplebot import DeltaBot
from telethon import TelegramClient
from telethon.sessions import StringSession

_scope = __name__.split(".", maxsplit=1)[0]


def sync(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        asyncio.new_event_loop().run_until_complete(func(*args, **kwargs))

    return wrapper


def getdefault(bot: DeltaBot, key: str, value: str = None) -> str:
    val = bot.get(key, scope=_scope)
    if val is None and value is not None:
        bot.set(key, value, scope=_scope)
        val = value
    return val


def set_config(bot: DeltaBot, key: str, value: str = None) -> None:
    bot.set(key, value, scope=_scope)


def get_client(bot: DeltaBot, session: str = None) -> TelegramClient:
    api_id = getdefault(bot, "api_id")
    api_hash = getdefault(bot, "api_hash")
    if session is None:
        session = getdefault(bot, "session")
    return TelegramClient(
        StringSession(session) if session else StringSession(),
        api_id=api_id,
        api_hash=api_hash,
    )
