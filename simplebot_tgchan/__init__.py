"""hooks, filters and commands definitions."""

import asyncio
import os
from tempfile import TemporaryDirectory
from threading import Thread

import simplebot
from deltachat import Chat, Contact, Message
from simplebot import DeltaBot
from simplebot.bot import Replies
from telethon import events
from telethon.tl.functions.channels import JoinChannelRequest
from telethon.tl.functions.messages import ImportChatInviteRequest

from .orm import Subscription, init, session_scope
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


@simplebot.hookimpl
def deltabot_start(bot: DeltaBot) -> None:
    path = os.path.join(os.path.dirname(bot.account.db_path), __name__)
    if not os.path.exists(path):
        os.makedirs(path)
    path = os.path.join(path, "sqlite.db")
    init(f"sqlite:///{path}")
    Thread(target=listen_to_telegram, args=(bot,), daemon=True).start()


@simplebot.hookimpl
def deltabot_member_removed(
    bot: DeltaBot, chat: Chat, contact: Contact, replies: Replies
) -> None:
    if bot.self_contact != contact and len(chat.get_contacts()) > 1:
        return

    with session_scope() as session:
        session.query(Subscription).filter_by(chat_id=chat.id).delete()


@simplebot.command(admin=True)
def sub(bot: DeltaBot, payload: str, message: Message, replies: Replies) -> None:
    """Subscribe chat to the given Telegram channel."""
    _sub(bot, payload, message, replies)


@sync
async def _sub(bot: DeltaBot, payload: str, message: Message, replies: Replies) -> None:
    if not getdefault(bot, "session"):
        replies.add(text="❌ You must log in first", quote=message)
        return

    if not message.chat.is_multiuser():
        replies.add(
            text="❌ Subscribing is supported in group chats only", quote=message
        )
        return

    args = payload.split(maxsplit=1)
    chan = args[0].rsplit("/", maxsplit=1)[-1]
    if "/joinchat/" in args[0]:
        request = ImportChatInviteRequest
    else:
        request = JoinChannelRequest
        chan = chan.strip("@").replace(" ", "_")
    filter_ = args[1] if len(args) == 2 else ""

    try:
        client = get_client(bot)
        await client.connect()
        await client(request(chan))
        with session_scope() as session:
            session.add(
                Subscription(chat_id=message.chat.id, chan=chan, filter=filter_)
            )
        replies.add(text=f"✔️ Subscribed to {chan}")
    except Exception as ex:
        bot.logger.exception(ex)
        replies.add(text=f"❌ Error: {ex}", quote=message)
    finally:
        await client.disconnect()


@simplebot.command(admin=True)
def unsub(bot: DeltaBot, payload: str, message: Message, replies: Replies) -> None:
    """Unsubscribe chat from the given Telegram channel."""
    _unsub(bot, payload, message, replies)


@sync
async def _unsub(
    bot: DeltaBot, payload: str, message: Message, replies: Replies
) -> None:
    with session_scope() as session:
        if payload:
            subs = (
                session.query(Subscription)
                .filter_by(chat_id=message.chat.id, chan=payload)
                .first()
            )
            if subs:
                session.delete(subs)
                replies.add(text=f"✔️ Unsubscribed from {payload}")
            else:
                replies.add(text=f"❌ Error: chat is not subscribed to {payload}")
        else:
            text = ""
            for subs in session.query(Subscription).filter_by(chat_id=message.chat.id):
                text += f"/unsub_{subs.chan}\n\n"
            if not text:
                text = "❌ No subscriptions in this chat"
            replies.add(text=text)


@sync
async def listen_to_telegram(bot: DeltaBot) -> None:
    if not getdefault(bot, "session"):
        bot.logger.warning("Telegram session not configured")
        return

    while True:
        bot.logger.debug("Checking Telegram")
        try:
            client = get_client(bot)
            await client.connect()
            dialogs = await client.get_dialogs()
            for dialog in reversed(dialogs):
                if (
                    dialog.unread_count <= 0
                    or not dialog.is_channel
                    or dialog.is_group
                    or not dialog.entity.username
                ):
                    continue
                messages = list(
                    reversed(
                        await client.get_messages(dialog, limit=dialog.unread_count)
                    )
                )
                if not messages:
                    continue
                bot.logger.debug(
                    f"Channel {dialog.name!r} has {len(messages)} new messages"
                )
                with session_scope() as session:
                    replies = Replies(bot, bot.logger)
                    for msg in messages:
                        if msg.text is None:
                            continue
                        args = dict(
                            text=msg.text,
                            sender=dialog.title or dialog.name or "Unknown",
                        )
                        with TemporaryDirectory() as tempdir:
                            if msg.file and msg.file.size < 1024**2 * 5:
                                args["filename"] = await msg.download_media(tempdir)
                            if not msg.text and not args.get("filename"):
                                continue
                            for subs in session.query(Subscription).filter_by(
                                chan=dialog.entity.username
                            ):
                                if subs.filter in msg.text:
                                    try:
                                        replies.add(
                                            **args, chat=bot.get_chat(int(subs.chat_id))
                                        )
                                        replies.send_reply_messages()
                                    except Exception as ex:
                                        bot.logger.exception(ex)
                await client.send_read_acknowledge(dialog, messages)
        except Exception as ex:
            bot.logger.exception(ex)
        finally:
            await client.disconnect()
        delay = int(getdefault(bot, "delay"))
        bot.logger.debug(f"Done checking Telegram, sleeping for {delay} seconds...")
        await asyncio.sleep(delay)
