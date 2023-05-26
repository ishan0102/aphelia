import os
import discord
from discord.ext import commands
from dotenv import load_dotenv
import asyncio

# Import the custom cog modules
from cogs.notion_cog import NotionCog
from cogs.labml_cog import LabMLCog

load_dotenv()

intents = discord.Intents.default()
intents.messages = True
intents.guilds = True
intents.message_content = True

bot = commands.Bot(command_prefix="/", intents=intents)


@bot.event
async def on_ready():
    print(f"We have logged in as {bot.user}")


# Load the cogs
bot.add_cog(NotionCog(bot))
bot.add_cog(LabMLCog(bot))


# Make sure to use the await keyword when adding cogs
async def start_bot():
    await bot.start(os.getenv("DISCORD_BOT_TOKEN"))


# Run the bot
if __name__ == "__main__":
    asyncio.run(start_bot())
