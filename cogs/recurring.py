import os
import random

import aiohttp
import discord
from discord import app_commands
from discord.ext import commands, tasks
from discord.ext.commands import Context
from rsrch import RsrchClient

from helpers import checks


class RecurringCog(commands.Cog, name="recurring"):
    def __init__(self, bot):
        self.bot = bot
        self.notification_channel = None
        self.hn = False
        self.rsrch_client = RsrchClient(token=os.getenv("NOTION_TOKEN"), database_id=os.getenv("NOTION_DATABASE_ID"))

    @commands.command(
        name="setnotifs",
        description="Set the channel for sending notifications.",
    )
    @checks.is_owner()
    async def set_notification_channel(self, context: Context, channel: discord.TextChannel):
        self.notification_channel = channel
        embed = discord.Embed(
            title=f"Notification channel set to {channel.mention}",
            color=0x9C84EF,
        )
        await context.send(embed=embed)
        await channel.send("This channel will now receive notifications.")

    @tasks.loop(hours=8.0)
    async def send_hn(self, channel):
        if not self.hn:
            return

        async with aiohttp.ClientSession() as session:
            async with session.get("https://hacker-news.firebaseio.com/v0/topstories.json") as request:
                if request.status == 200:
                    top_stories = await request.json()
                    top_stories = top_stories[:10]
                    data = []
                    for i, story in enumerate(top_stories):
                        async with session.get(
                            f"https://hacker-news.firebaseio.com/v0/item/{story}.json"
                        ) as story_request:
                            story_data = await story_request.json()
                            title = story_data.get("title")
                            score = story_data.get("score")
                            url = story_data.get("url")
                            discussion = "https://news.ycombinator.com/item?id=" + str(story)
                            data.append(f"{i}. [{title}]({url}) ({score}, [discussion]({discussion}))")
                    embed = discord.Embed(title="Hacker News Top Stories", description="\n".join(data), color=0x9C84EF)
                    await channel.send(embed=embed)
                else:
                    embed = discord.Embed(
                        title="Error!",
                        description="There is something wrong with the API, please try again later",
                        color=0xE02B2B,
                    )
                    await channel.send(embed=embed)

    @commands.hybrid_command(
        name="hn",
        description="Enable or disable Hacker News notifications.",
    )
    @checks.is_owner()
    @app_commands.describe(enable_choice="Your choice (enable/disable)")
    async def hn(self, context: Context, enable_choice: str):
        if enable_choice not in ["enable", "disable"]:
            embed = discord.Embed(
                title="Invalid choice",
                description="You must choose between `enable` and `disable`.",
                color=0xE02B2B,
            )
            await context.send(embed=embed)
            return

        if not self.notification_channel:
            embed = discord.Embed(
                title="Notification channel not set",
                description="You must set a notification channel using the `setnotifs` command.",
                color=0xE02B2B,
            )
            await context.send(embed=embed)
            return

        if enable_choice == "enable":
            self.hn = True
            self.send_hn.start(self.notification_channel)
        elif enable_choice == "disable":
            self.hn = False
            self.send_hn.cancel()

        embed = discord.Embed(
            title=f"Hacker News notifications `{enable_choice}d`",
            color=0x9C84EF,
        )
        await context.send(embed=embed)

    @tasks.loop(hours=24.0)
    async def send_random_paper(self, channel):
        papers = self.rsrch_client.fetch_table()
        if not papers:
            return

        random_paper = random.choice(papers)
        title, url, date, authors = random_paper
        description = f"Authors: {authors}\nDate: {date}"
        embed = discord.Embed(title=f"Random paper to read: {title}", url=url, description=description, color=0x9C84EF)
        await channel.send(embed=embed)

    @commands.hybrid_command(
        name="paper",
        description="Enable or disable daily random paper notifications.",
    )
    @checks.is_owner()
    @app_commands.describe(enable_choice="Your choice (enable/disable)")
    async def paper(self, context: Context, enable_choice: str):
        if enable_choice not in ["enable", "disable"]:
            embed = discord.Embed(
                title="Invalid choice",
                description="You must choose between `enable` and `disable`.",
                color=0xE02B2B,
            )
            await context.send(embed=embed)
            return

        if not self.notification_channel:
            embed = discord.Embed(
                title="Notification channel not set",
                description="You must set a notification channel using the `setnotifs` command.",
                color=0xE02B2B,
            )
            await context.send(embed=embed)
            return

        if enable_choice == "enable":
            self.send_random_paper.start(self.notification_channel)
        elif enable_choice == "disable":
            self.send_random_paper.cancel()

        embed = discord.Embed(
            title=f"Daily random paper notifications `{enable_choice}d`",
            color=0x9C84EF,
        )
        await context.send(embed=embed)


async def setup(bot):
    await bot.add_cog(RecurringCog(bot))
