from typing import Final
from dotenv import load_dotenv
from lib.logger import log
import os
import discord

load_dotenv()
TOKEN: Final[str] = os.getenv("DISCORD_TOKEN")
client = discord.Bot()


@client.event
async def on_ready():
    log(f'Logged in as {client.user}')
    client.load_extension('lib.commands')
    await client.sync_commands()


def main() -> None:
    client.run(token=TOKEN)


if __name__ == "__main__":
    main()
