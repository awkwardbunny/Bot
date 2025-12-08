import base64
import logging
import tempfile
from abc import abstractmethod
from datetime import datetime
from logging import Logger
from pathlib import Path
import json

from PIL import Image
from escpos.printer import Network

from signalbot import Command, Context, SignalBot, enable_console_logging, triggered

botLogger = logging.getLogger("BOT")
botLogger.setLevel(logging.INFO)


class CommandWithHelpMessage(Command):
    @abstractmethod
    def help_message(self) -> str:
        pass


class HelpCommand(CommandWithHelpMessage):
    def __init__(self, logger: Logger) -> None:
        super().__init__()
        self.logger = logger.getChild("HelpCommand")
        self.logger.info("Registering HELP")

    def help_message(self) -> str:
        return "help: 🆘 Show info about commands."

    @triggered("!help")
    async def handle(self, c: Context) -> None:
        help_msg = "Available commands:\n"
        cmd: CommandWithHelpMessage
        for cmd, _, _, _ in self.bot.commands:
            help_msg += f"\t - {cmd.help_message()}\n"
        await c.send(help_msg)


class TodoCommand(CommandWithHelpMessage):
    """Command handler for printing to-do slips."""

    def __init__(self, logger: Logger, config: dict) -> None:
        super().__init__()
        self.logger = logger.getChild("TodoCommand")
        self.logger.info("Registering TODO")

        device = config.get("device", "/dev/usb/lp0")
        profile = config.get("profile", "TM-T88IV")
        self.printer = Network(device, profile=profile)
        self.printer.set(align="left")

        self.logger.info("Printer initialized")

        # self.printer.textln("Started")
        # self.printer.cut()
        self.printer.close()

    def help_message(self) -> str:
        return "todo: 🖨️ Print out a to-do slip."

    # @triggered("!todo")
    async def handle(self, ctx: Context) -> None:
        await self.bot.receipt(ctx.message, "read")

        msg = ctx.message.text
        self.logger.debug(f"Received '{msg}'")
        if not msg:
            return

        if msg.split()[0].lower() != "!todo":
            return

        if len(msg.split()) < 2:
            await self.bot.react(ctx.message, "❗")
            await ctx.send("What todo?")
            return

        msg = msg[5:]

        short = msg if len(msg) < 30 else msg[:20] + "..."
        self.logger.info(f"NEW TODO:{short}")

        # Print
        ts = datetime.fromtimestamp(ctx.message.timestamp / 1000)
        ts = ts.strftime("[%m/%d/%Y (%a) -- %H:%M:%S]\n")

        self.printer.open()
        self.printer.textln(ts)

        self.printer.set(bold=True)
        self.printer.textln("TODO: ")
        self.printer.set(bold=False)
        self.printer.textln(msg)

        # Print images
        if ctx.message.base64_attachments:
            for a, name in zip(ctx.message.base64_attachments, ctx.message.attachments_local_filenames):
                match Path(name).suffix:
                    case ".png" | ".jpg" | ".jpeg" | ".gif" | ".bmp":
                        with tempfile.NamedTemporaryFile() as f:
                            f.write(base64.b64decode(a))
                            img = Image.open(f)
                            ratio = img.height / img.width
                            new_height = int(ratio * 512)
                            new_img = img.resize((512, new_height), Image.Resampling.LANCZOS)

                            self.printer.image(new_img)
                        self.printer.textln()

        self.printer.cut()
        self.printer.close()
        await self.bot.react(ctx.message, "🖨")


def main():
    enable_console_logging()

    # Load configuration from config.json
    botLogger.info("Loading config...")
    with open("config.json", "r") as f:
        cfg = json.load(f)

    logFile = cfg.get("logFile", "bot.log")
    fileLogger = logging.FileHandler(logFile)
    fmtr = logging.Formatter("%(asctime)s [%(levelname)-5.5s] %(name)s:%(message)s")
    fileLogger.setFormatter(fmtr)
    botLogger.addHandler(fileLogger)

    bot = SignalBot(cfg["bot_config"])
    bot.register(HelpCommand(botLogger), contacts=cfg["allow_from"])
    bot.register(TodoCommand(botLogger, cfg["printer_config"]), contacts=cfg["allow_from"])

    botLogger.info("Starting bot...")
    bot.start()


if __name__ == "__main__":
    main()
