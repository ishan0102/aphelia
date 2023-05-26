from discord.ext import commands
from rsrch import popular
import asyncio


class LabMLCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.send_daily_paper = False
        self.bot.remove_listener(self.on_message, "on_message")
        self.bot.add_listener(self.on_message, "on_message")

    async def on_message(self, message):
        if message.author == self.bot.user:
            return

        content = message.content.lower()
        if content == "start sending daily papers":
            self.send_daily_paper = True
            await self.start_loop(message.channel)
        elif content == "stop sending daily papers":
            self.send_daily_paper = False

    async def start_loop(self, channel):
        while self.send_daily_paper:
            formatted_papers = self.fetch_and_format_papers()
            if formatted_papers:
                await channel.send(f"{formatted_papers}")
            await asyncio.sleep(86400)  # sleep for 24 hours

    def fetch_and_format_papers(self):
        # Grab popular papers
        papers = popular("daily", 1)

        # Extract relevant information from each paper
        formatted_papers = "## Paper of the day\n"
        for paper in papers:
            title = paper.title
            date = paper.published.date().isoformat()
            url = paper.entry_id
            formatted_papers += f"**Title:** {title}\n**Date:** {date}\n**URL:** {url}\n\n"

        return formatted_papers
