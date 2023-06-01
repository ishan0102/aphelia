import asyncio

import aiohttp
import discord
from discord import app_commands
from discord.ext import commands
from discord.ext.commands import Context

from helpers import checks


class RecurringCog(commands.Cog, name="recurring"):
    def __init__(self, bot):
        self.bot = bot
        self.hn = False
        self.notification_channel = None

    @commands.command(
        name="notifschannel",
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

    async def start_loop(self, channel):
        while self.hn:
            async with aiohttp.ClientSession() as session:
                async with session.get("https://hacker-news.firebaseio.com/v0/topstories.json") as request:
                    if request.status == 200:
                        top_stories = await request.json()
                        top_stories = top_stories[:5]
                        embed = discord.Embed(title="Hacker News Top Stories", color=0x9C84EF)
                        data = []
                        for i, story in enumerate(top_stories):
                            async with session.get(
                                f"https://hacker-news.firebaseio.com/v0/item/{story}.json"
                            ) as story_request:
                                story_data = await story_request.json()
                                title = story_data.get("title")
                                score = story_data.get("score")
                                url = story_data.get("url")
                                data.append(f"{i}. [{title}]({url}) ({score})")
                        embed.add_field(name="", value="\n".join(data), inline=False)
                        await channel.send(embed=embed)
                    else:
                        embed = discord.Embed(
                            title="Error!",
                            description="There is something wrong with the API, please try again later",
                            color=0xE02B2B,
                        )
                        await channel.send(embed=embed)
            await asyncio.sleep(28800)  # 8 hours

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
                description="You must set a notification channel using the `notifschannel` command.",
                color=0xE02B2B,
            )
            await context.send(embed=embed)
            return

        if enable_choice == "enable":
            self.hn = True
            await self.start_loop(self.notification_channel)
        elif enable_choice == "disable":
            self.hn = False

        embed = discord.Embed(
            title=f"Hacker News notifications `{enable_choice}d`",
            color=0x9C84EF,
        )
        await context.send(embed=embed)


async def setup(bot):
    await bot.add_cog(RecurringCog(bot))
