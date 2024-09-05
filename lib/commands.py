from distutils.util import strtobool
from lib.logger import log
from discord.ext import commands
from typing import Final
from sys import platform
import os
import discord
import subprocess

CHANNEL_ID: Final[int] = int(os.getenv("CHANNEL_ID"))
SERVER_PATH: Final[str] = os.getenv("SERVER_PATH")
CHANNEL_STATUS: Final[bool] = bool(strtobool(os.getenv("CHANNEL_STATUS")))

if platform == "win32":
    SERVER_OS = "win"
elif platform == "linux":
    SERVER_OS = "unix"


async def channel_status(ctx, status):
    if CHANNEL_STATUS:
        log("Changing channel status")

        guild = ctx.guild
        voice_channel = guild.get_channel(CHANNEL_ID)
        match status:
            case "start":
                message = "✅ ⁞ server status: ON"
            case "stop":
                message = "🚫 ⁞ server status: OFF"
            case "starting":
                message = "⏳ ⁞ server status: Starting"
            case _:
                message = "❓ ⁞ server status: Unknown"

        if voice_channel:
            await voice_channel.edit(name=message)

        log("Channel status changed")

    else:
        log("Skipping channel status changing")


class Commands(commands.Cog):
    def __init__(self, bot):
        self.server_process = None
        self.bot = bot

    @commands.slash_command(name="ping", description="Ping the bot")
    async def ping(self, ctx: discord.ApplicationContext):
        await ctx.respond(f'Pong! {self.bot.latency}ms')

    @commands.slash_command(name="status", description="Status of server")
    async def status(self, ctx: discord.ApplicationContext):
        if self.server_process is None:
            await ctx.respond("Server off")
        else:
            await ctx.respond("Server on")

    @commands.slash_command(name="start", description="Start minecraft server")
    async def start(self, ctx: discord.ApplicationContext):
        log("Starting server")
        await ctx.respond("Starting server")

        command = [
            "java",
            "@user_jvm_args.txt",
            f"@libraries/net/minecraftforge/forge/1.20.1-47.2.0/{SERVER_OS}_args.txt",
            "nogui"
        ]

        if not self.server_process:
            self.server_process = subprocess.Popen(command, cwd=SERVER_PATH, stdout=subprocess.PIPE,
                                                   stderr=subprocess.PIPE, text=True)
            await channel_status(ctx, "starting")

            try:
                for line in self.server_process.stdout:
                    if "Done" in line:  # Adjust this condition based on the actual server start message
                        log("Minecraft server has started!")
                        await ctx.send("Minecraft server has started!")
                        await channel_status(ctx, "start")
                        break
            except Exception as e:
                log("Server crashed")
                await ctx.send("Server crashed")
                await channel_status(ctx, "stop")

        else:
            log("Server is already running")
            await ctx.send("Server is already running")

    @commands.slash_command(name="stop", description="Stop minecraft server")
    async def stop(self, ctx: discord.ApplicationContext):
        if self.server_process:
            log("Stopping server")
            await ctx.respond("Stopping server")
            self.server_process.terminate()
            await ctx.send("Server has stopped")
            await channel_status(ctx, "stop")
            self.server_process = None
        else:
            log("Server is currently stopped")
            await ctx.respond("Server is currently stopped")


def setup(bot):
    bot.add_cog(Commands(bot))
