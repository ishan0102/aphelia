import io
import os
import random
import re
import sys

import discord
from discord import app_commands
from discord.ext import commands
from discord.ext.commands import Context
from rsrch import RsrchClient

from helpers import checks


class NotionCog(commands.Cog, name="notion"):
    def __init__(self, bot):
        self.bot = bot
        self.rsrch_client = RsrchClient(token=os.getenv("NOTION_TOKEN"), database_id=os.getenv("NOTION_DATABASE_ID"))

    @commands.hybrid_command(
        name="upload",
        description="Upload research papers to Notion.",
    )
    @checks.is_owner()
    @app_commands.describe(message="A message containing arXiv links to upload.")
    async def upload(self, context: Context, *, message: str):
        # Redirect stdout to a StringIO object
        original_stdout = sys.stdout
        sys.stdout = captured_stdout = io.StringIO()

        # Use regular expressions to search for URLs in the message content
        urls = re.findall("(?P<url>https?://[^\s]+)", message)

        # Push the URLs to push_papers
        try:
            self.rsrch_client.upload(urls)
        except ValueError:
            embed = discord.Embed(
                title="No valid arXiv URLs found",
                color=0xE02B2B,
            )
            await context.send(embed=embed)
            return

        # Reset stdout to the original value
        sys.stdout = original_stdout

        # Get the captured output and send it to the channel if it exists
        output = captured_stdout.getvalue()

        # Create an embed with the output
        if output and "-" in output:
            embed = discord.Embed(
                title="**Uploaded papers**",
                color=0x9C84EF,
            )

            data = [line for line in output.splitlines() if line.startswith("-")]
            embed.add_field(name="", value="\n".join(data), inline=False)
        else:
            embed = discord.Embed(
                title="No papers to upload",
                color=0xE02B2B,
            )

        await context.send(embed=embed)

    @commands.command(
        name="fetch",
        description="Retrieve a random research paper from Notion.",
    )
    @checks.is_owner()
    async def get_paper(self, context: Context):
        papers = self.rsrch_client.fetch_table()
        if not papers:
            embed = discord.Embed(
                title="No papers found",
                color=0xE02B2B,
            )
            await context.send(embed=embed)
            return

        random_paper = random.choice(papers)
        title, url, date, authors = random_paper
        description = f"Authors: {authors}\nDate: {date}"
        embed = discord.Embed(title=f"{title}", url=url, description=description, color=0x9C84EF)
        await context.send(embed=embed)


async def setup(bot):
    await bot.add_cog(NotionCog(bot))
