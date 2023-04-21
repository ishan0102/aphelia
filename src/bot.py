import os
import sys
import discord
from discord.ext import commands
from dotenv import load_dotenv

# Import the custom cog module
from cogs.rsrch_cog import RsrchCog

load_dotenv()

intents = discord.Intents.default()
intents.messages = True
intents.guilds = True
intents.message_content = True

bot = commands.Bot(command_prefix="/", intents=intents)


@bot.event
async def on_ready():
    print(f"We have logged in as {bot.user}")


# Load the cog
bot.add_cog(RsrchCog(bot))

bot.run(os.getenv("DISCORD_BOT_TOKEN"))
