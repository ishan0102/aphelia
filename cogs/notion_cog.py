import io
import re
import sys

from discord.ext import commands
from discord.ext.commands import Context
from discord import app_commands
import rsrch
import discord

from helpers import checks


class NotionCog(commands.Cog, name="notion"):
    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command(
        name="upload",
        description="Upload research papers to Notion.",
    )
    @checks.is_owner()
    @app_commands.describe(message="A message containing arXiv links to upload.")
    async def upload(self, context: Context, message: str):
        """
        This function executes whenever a message is received.

        :param message: The message context.
        """

        # Redirect stdout to a StringIO object
        original_stdout = sys.stdout
        sys.stdout = captured_stdout = io.StringIO()

        # Use regular expressions to search for URLs in the message content
        urls = re.findall("(?P<url>https?://[^\s]+)", message)

        # Push the URLs to push_papers
        rsrch.upload(urls)

        # Reset stdout to the original value
        sys.stdout = original_stdout

        # Get the captured output and send it to the channel
        output = captured_stdout.getvalue()
        embed = discord.Embed(
            title="**Uploaded papers**",
            color=0x9C84EF,
        )
        embed.set_footer(text=output)
        if output and "-" in output:
            await context.send(embed=embed)


async def setup(bot):
    await bot.add_cog(NotionCog(bot))
