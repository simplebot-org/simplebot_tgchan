from simplebot import DeltaBot

from .util import get_client, set_config, sync


class login:
    """Login on Telegram."""

    def add_arguments(self, parser) -> None:
        parser.add_argument("--session", help="set a saved session")

    def run(self, bot: DeltaBot, args, out) -> None:
        if args.session:
            set_config(bot, "session", args.session)
            out.line("Session set")
        else:
            self._login(bot, out)

    @staticmethod
    @sync
    async def _login(bot: DeltaBot, out) -> None:
        phone = input("Please enter your phone: ").replace(" ", "")
        if "+" not in phone:
            out.fail("Phone number must include country code, example: +5312345678")
        try:
            client = get_client(bot)
            await client.connect()
            phone_code_hash = (await client.send_code_request(phone)).phone_code_hash
            out.line("You should receive a code from Telegram")
            code = input("Please enter the code you received: ")
            await client.sign_in(phone, code, phone_code_hash=phone_code_hash)
            session = client.session.save()
            set_config(bot, "session", session)
            out.line("You have logged in successfully. Your session is:")
            out.line(session)
        except Exception as ex:
            bot.logger.exception(ex)
            out.fail(str(ex))
        finally:
            await client.disconnect()
