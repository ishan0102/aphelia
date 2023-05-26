from discord.ext import commands
from rsrch import popular


class LabMLCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.bot.add_listener(self.on_message, "on_message")

    async def on_message(self, message):
        if message.author == self.bot.user or message.channel.name != "rsrch":
            return

        # Grab popular papers
        papers = popular("daily", 1)

        # Extract relevant information from each paper
        formatted_papers = "## Paper of the day\n"
        for paper in papers:
            title = paper.title
            date = paper.published.date().isoformat()
            url = paper.entry_id
            formatted_papers += f"**Title:** {title}\n**Date:** {date}\n**URL:** {url}\n\n"

        # Send the formatted table to the channel
        if formatted_papers:
            await message.channel.send(f"{formatted_papers}")

        await self.bot.process_commands(message)
