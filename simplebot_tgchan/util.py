import asyncio
from functools import wraps

from simplebot import DeltaBot
from telethon import TelegramClient
from telethon.sessions import StringSession


def sync(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        asyncio.new_event_loop().run_until_complete(func(*args, **kwargs))

    return wrapper


def getdefault(bot: DeltaBot, key: str, value: str = None) -> str:
    scope = __name__.split(".")[0]
    val = bot.get(key, scope=scope)
    if val is None and value is not None:
        bot.set(key, value, scope=scope)
        val = value
    return val


def set_config(bot: DeltaBot, key: str, value: str = None) -> None:
    bot.set(key, value, scope=__name__.split(".")[0])


def get_client(bot: DeltaBot) -> TelegramClient:
    api_id = getdefault(bot, "api_id")
    api_hash = getdefault(bot, "api_hash")
    session = getdefault(bot, "session")
    return TelegramClient(
        StringSession(session) if session else StringSession(),
        api_id=api_id,
        api_hash=api_hash,
    )
