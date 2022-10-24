"""hooks, filters and commands definitions."""

import asyncio
import os
import time
from tempfile import TemporaryDirectory
from threading import Thread

import simplebot
from deltachat import Chat, Contact, Message
from simplebot import DeltaBot
from simplebot.bot import Replies
from telethon import TelegramClient
from telethon.tl.functions.channels import JoinChannelRequest
from telethon.tl.functions.messages import ImportChatInviteRequest
from telethon.tl.types import PeerChannel

from .instantview import page2html
from .orm import Channel, Subscription, init, session_scope
from .subcommands import login
from .util import get_client, getdefault, set_config, sync


@simplebot.hookimpl
def deltabot_init_parser(parser) -> None:
    parser.add_subcommand(login)


@simplebot.hookimpl
def deltabot_init(bot: DeltaBot) -> None:
    getdefault(bot, "api_id", "")
    getdefault(bot, "api_hash", "")
    getdefault(bot, "delay", str(60 * 5))
    getdefault(bot, "max_size", str(1024**2 * 5))
    allow_sub = getdefault(bot, "allow_subscriptions", "1") == "1"
    bot.commands.register(func=sub, admin=not allow_sub)
    bot.commands.register(func=unsub, admin=not allow_sub)


@simplebot.hookimpl
def deltabot_start(bot: DeltaBot) -> None:
    path = os.path.join(os.path.dirname(bot.account.db_path), __name__)
    if not os.path.exists(path):
        os.makedirs(path)
    path = os.path.join(path, "sqlite.db")
    init(f"sqlite:///{path}")
    Thread(target=listen_to_telegram, args=(bot,), daemon=True).start()


@simplebot.hookimpl
def deltabot_member_removed(bot: DeltaBot, chat: Chat, contact: Contact) -> None:
    if bot.self_contact != contact and len(chat.get_contacts()) > 1:
        return

    empty_channels = []
    with session_scope() as session:
        for subs in session.query(Subscription).filter_by(chat_id=chat.id):
            channel = subs.channel
            session.delete(subs)
            if not channel.subscriptions:
                bot.logger.debug(
                    f"Removing channel without subscriptions: {channel.id}"
                )
                empty_channels.append(channel.id)
                session.delete(channel)

    if empty_channels:
        leave_channels(bot, *empty_channels)


def sub(bot: DeltaBot, payload: str, message: Message, replies: Replies) -> None:
    """Subscribe chat to the given Telegram channel."""
    if not getdefault(bot, "session"):
        replies.add(text="❌ You must log in first", quote=message)
    elif not payload:
        replies.add(text="❌ You must provide a channel link or name", quote=message)
    elif not message.chat.is_multiuser():
        replies.add(
            text="❌ Subscribing is supported in group chats only", quote=message
        )
    else:
        _sub(bot, payload, message, replies)


@sync
async def _sub(bot: DeltaBot, payload: str, message: Message, replies: Replies) -> None:
    args = payload.split(maxsplit=1)
    chan = args[0].rsplit("/", maxsplit=1)[-1]
    if "/joinchat/" in args[0]:
        request = ImportChatInviteRequest
    elif chan.startswith("+"):
        request = ImportChatInviteRequest
        chan = chan[1:]
    else:
        request = JoinChannelRequest
        chan = chan.lstrip("@").replace(" ", "_")
    filter_ = args[1] if len(args) == 2 else ""

    try:
        client = get_client(bot)
        await client.connect()
        channel = (await client(request(chan))).chats[0]
        assert channel.broadcast, "Invalid channel"
        set_config(bot, "session", client.session.save())
        with session_scope() as session:
            if not session.query(Channel).filter_by(id=channel.id).first():
                msgs = await client.get_messages(channel, limit=1)
                msg_id = msgs[0].id if msgs else 0
                session.add(
                    Channel(id=channel.id, title=channel.title, last_msg=msg_id)
                )
            session.add(
                Subscription(
                    chat_id=message.chat.id, chan_id=channel.id, filter=filter_
                )
            )
        replies.add(text=f"✔️ Subscribed to {channel.title!r}")
    except Exception as ex:
        bot.logger.exception(ex)
        replies.add(text=f"❌ Error: {ex}", quote=message)
    finally:
        await client.disconnect()


def unsub(bot: DeltaBot, payload: str, message: Message, replies: Replies) -> None:
    """Unsubscribe chat from the given Telegram channel.

    If no channel is given, list all channels that can be unsubscribed in the current chat.
    """
    empty_channels = []
    with session_scope() as session:
        if payload:
            chan_id = int(payload.replace("n", "-"))
            subs = (
                session.query(Subscription)
                .filter_by(chat_id=message.chat.id, chan_id=chan_id)
                .first()
            )
            if subs:
                channel = subs.channel
                title = channel.title
                session.delete(subs)
                if not channel.subscriptions:
                    bot.logger.debug(
                        f"Removing channel without subscriptions: {channel.id}"
                    )
                    empty_channels.append(channel.id)
                    session.delete(channel)
                replies.add(text=f"✔️ Unsubscribed from {title!r}")
            else:
                replies.add(
                    text="❌ Error: chat is not subscribed to that channel",
                    quote=message,
                )
        else:
            text = ""
            for subs in session.query(Subscription).filter_by(chat_id=message.chat.id):
                chan = str(subs.chan_id).replace("-", "n")
                text += f"{subs.channel.title}\n/unsub_{chan}\n\n"
            if not text:
                text = "❌ No subscriptions in this chat"
            replies.add(text=text)

    if empty_channels:
        leave_channels(bot, *empty_channels)


@sync
async def listen_to_telegram(bot: DeltaBot) -> None:
    if not getdefault(bot, "session"):
        bot.logger.warning("Telegram session not configured")
        return

    while True:
        bot.logger.debug("Checking Telegram")
        start = time.time()
        try:
            await check_channels(bot)
        except Exception as ex:
            bot.logger.exception(ex)
        elapsed = int(time.time() - start)
        delay = max(int(getdefault(bot, "delay")) - elapsed, 30)
        bot.logger.debug(
            f"Done checking Telegram after {elapsed} seconds, sleeping for {delay} seconds..."
        )
        await asyncio.sleep(delay)


async def check_channels(bot: DeltaBot) -> None:
    try:
        client = get_client(bot)
        await client.connect()
        with session_scope() as session:
            bot.logger.debug("Channels to check: %s", session.query(Channel).count())
            for chan in session.query(Channel):
                try:
                    await check_channel(bot, client, chan)
                    await asyncio.sleep(0.5)
                except Exception as ex:
                    bot.logger.exception(ex)
    finally:
        await client.disconnect()


async def check_channel(bot: DeltaBot, client: TelegramClient, dbchan: Channel) -> None:
    channel = await client.get_entity(PeerChannel(dbchan.id))
    dbchan.title = channel.title
    messages = list(
        reversed(await client.get_messages(channel, min_id=dbchan.last_msg, limit=20))
    )
    bot.logger.debug(f"Channel {channel.title!r} has {len(messages)} new messages")
    for message in messages:
        try:
            await tg2dc(bot, client, message, dbchan)
        except Exception as ex:
            bot.logger.exception(ex)
        dbchan.last_msg = message.id
    await client.send_read_acknowledge(channel, messages)


async def tg2dc(bot: DeltaBot, client: TelegramClient, msg, dbchan: Channel) -> None:
    if msg.text is None:
        return
    replies = Replies(bot, bot.logger)
    args = dict(
        text=msg.text,
        sender=dbchan.title or "Unknown",
    )
    with TemporaryDirectory() as tempdir:
        if msg.file and msg.file.size <= int(getdefault(bot, "max_size")):
            args["filename"] = await msg.download_media(tempdir)
            if args["filename"] and msg.sticker:
                args["viewtype"] = "sticker"
        if msg.web_preview and msg.web_preview.cached_page:
            args["html"] = await page2html(
                msg.web_preview.cached_page.blocks,
                client=client,
                msg=msg,
                logger=bot.logger,
            )
        if not any([args.get("text"), args.get("filename"), args.get("html")]):
            return
        for subs in dbchan.subscriptions:
            if subs.filter in msg.text:
                try:
                    replies.add(**args, chat=bot.get_chat(int(subs.chat_id)))
                    replies.send_reply_messages()
                except Exception as ex:
                    bot.logger.exception(ex)


@sync
async def leave_channels(bot, *args) -> None:
    try:
        client = get_client(bot)
        await client.connect()
        for chan_id in args:
            await client.delete_dialog(PeerChannel(chan_id))
    except Exception as ex:
        bot.logger.exception(ex)
    finally:
        await client.disconnect()
