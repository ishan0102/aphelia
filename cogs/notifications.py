import asyncio
import os
import random
import time
from datetime import datetime, timedelta

import aiohttp
import discord
from discord import app_commands
from discord.ext import commands, tasks
from discord.ext.commands import Context
from discord.utils import format_dt, utcnow
from rsrch import RsrchClient

from helpers import checks


async def fetch_hn_top_stories(session):
    async with session.get("https://hacker-news.firebaseio.com/v0/topstories.json") as request:
        if request.status == 200:
            return await request.json()
        return None


async def send_error_message(channel, title, description):
    embed = discord.Embed(title=title, description=description, color=0xE02B2B)
    await channel.send(embed=embed)


async def validate_enable_choice(context, enable_choice, notification_channel):
    if enable_choice not in ["enable", "disable"]:
        await send_error_message(context, "Invalid choice", "You must choose between `enable` and `disable`.")
        return False

    if not notification_channel:
        await send_error_message(
            context,
            "Notification channel not set",
            "You must set a notification channel using the `setnotifs` command.",
        )
        return False

    return True


class NotificationsCog(commands.Cog, name="notifications"):
    def __init__(self, bot):
        self.bot = bot
        self.notification_channel = None
        self.reminders = []
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

    async def send_reminder(self, channel: discord.TextChannel, reminder_name: str) -> None:
        await channel.send(f"🔔 Reminder: {reminder_name} 🔔")

    @commands.command(
        name="remindme",
        description="Sets a reminder for you.",
    )
    async def remindme(self, context, time: int, *, name: str) -> None:
        if not self.notification_channel:
            await send_error_message(
                context,
                "Notification channel not set",
                "You must set a notification channel using the `setnotifs` command.",
            )
            return

        await context.send(content=f"Reminder set for `{name}` in `{time}` minutes.")
        reminder_time = datetime.now() + timedelta(minutes=time)
        self.reminders.append((context.author, reminder_time, name))
        asyncio.get_event_loop().call_later(
            time * 60, asyncio.create_task, self.send_reminder(self.notification_channel, name)
        )

    @commands.command(
        name="reminders",
        description="Lists all current reminders.",
    )
    async def reminders(self, context: Context) -> None:
        if not self.reminders:
            embed = discord.Embed(
                title="Reminders",
                description="No reminders set at the moment.",
                color=0x9C84EF,
            )
        else:
            embed = discord.Embed(
                title="Reminders",
                color=0x9C84EF,
            )
            for reminder in self.reminders:
                user = reminder[0]
                reminder_time_left = format_dt(reminder[1], "R")
                reminder_name = reminder[2]

                embed.add_field(
                    name=f"Reminder: {reminder_name}",
                    value=f"Time left: {reminder_time_left}\nSet by: {user.name}",
                    inline=False,
                )

        await context.send(embed=embed)

    @tasks.loop(hours=6.0)
    async def send_hn(self, channel):
        if not self.hn:
            return

        async with aiohttp.ClientSession() as session:
            top_stories = await fetch_hn_top_stories(session)
            if not top_stories:
                await send_error_message(
                    channel, "Error!", "There is something wrong with the API, please try again later"
                )

            top_stories = top_stories[:10]
            data = []
            for i, story in enumerate(top_stories):
                async with session.get(f"https://hacker-news.firebaseio.com/v0/item/{story}.json") as story_request:
                    story_data = await story_request.json()
                    title = story_data.get("title")
                    score = story_data.get("score")
                    post_time = story_data.get("time")
                    url = story_data.get("url")
                    descendants = story_data.get("descendants")

                    hours_ago = round((time.time() - post_time) / 3600)
                    comments_url = "https://news.ycombinator.com/item?id=" + str(story)
                    data.append(
                        f"{i}. [{title}]({url}) ({score} upvotes, {hours_ago} hours ago, [{descendants} comments]({comments_url}))"
                    )
            embed = discord.Embed(title="Hacker News Top Stories", description="\n".join(data), color=0x9C84EF)
            await channel.send(embed=embed)

    @commands.hybrid_command(
        name="hn",
        description="Enable or disable Hacker News notifications.",
    )
    @checks.is_owner()
    @app_commands.describe(enable_choice="Your choice (enable/disable)")
    async def hn(self, context: Context, enable_choice: str):
        if not await validate_enable_choice(context, enable_choice, self.notification_channel):
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
        if not await validate_enable_choice(context, enable_choice, self.notification_channel):
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
    await bot.add_cog(NotificationsCog(bot))
