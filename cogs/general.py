from datetime import datetime

import discord
import openai
from discord.ext import commands
from discord.ext.commands import Context


class General(commands.Cog, name="general"):
    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command(name="help", description="List all commands.")
    async def help(self, context: Context) -> None:
        prefix = self.bot.config["prefix"]
        embed = discord.Embed(title="Help", description="List of available commands:", color=0x9C84EF)
        for i in self.bot.cogs:
            cog = self.bot.get_cog(i.lower())
            commands = cog.get_commands()
            data = []
            for command in commands:
                description = command.description.partition("\n")[0]
                data.append(f"{prefix}{command.name} - {description}")
            help_text = "\n".join(data)
            embed.add_field(name=i.capitalize(), value=f"```{help_text}```", inline=False)
        await context.send(embed=embed)

    @commands.hybrid_command(
        name="ping",
        description="Check if the bot is alive.",
    )
    async def ping(self, context: Context) -> None:
        """
        Check if the bot is alive.
        """
        embed = discord.Embed(
            title="🏓 Pong!",
            description=f"The bot latency is {round(self.bot.latency * 1000)}ms.",
            color=0x9C84EF,
        )
        await context.send(embed=embed)

    @commands.hybrid_command(
        name="invite",
        description="Get the bot's invite link.",
    )
    async def invite(self, context: Context) -> None:
        """
        Get the invite link of the bot to be able to invite it.
        """
        embed = discord.Embed(
            description=f"Invite me by clicking [here](https://discordapp.com/oauth2/authorize?&client_id={self.bot.config['application_id']}&scope=bot+applications.commands&permissions={self.bot.config['permissions']}).",
            color=0x9C84EF,
        )
        try:
            # To know what permissions to give to your bot, please see here: https://discordapi.com/permissions.html and remember to not give Administrator permissions.
            await context.send(embed=embed)
        except discord.Forbidden:
            await context.send(embed=embed)

    @commands.hybrid_command(
        name="source",
        description="Get the bot's source code.",
    )
    async def source(self, context: Context) -> None:
        """
        Get the source code of the bot.
        """
        embed = discord.Embed(
            description=f"You can find my source code [here](https://github.com/ishan0102/aphelia).",
            color=0x9C84EF,
        )
        await context.send(embed=embed)

    @commands.command(
        name="countdown",
        description="Generate a countdown timer.",
    )
    async def countdown(self, context: Context, *, message: str) -> None:
        if len(message) > 100:
            await context.send("Please provide a shorter description. I'm trying to save my tokens!")
            return

        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {
                    "role": "system",
                    "content": "You generate countdown timers. Be as concise as possible, provide no additional information apart from the link.",
                },
                {
                    "role": "user",
                    "content": "Generate a link like https://www.countdowns.live/?date=2024-01-01&time=00:00&desc=2024&timezone=America/Los_Angeles&style=fractional&bg=forest.gif. Use user's description for desc and choose bg from [forest.gif dystopian.gif bedroom.gif castle.gif lofigirl.gif bridge.png overlook.png palace.png star.png cityscape.png black.png].",
                },
                {
                    "role": "user",
                    "content": f"Generate a link for this description: {message}. Now is {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}.",
                },
            ],
        )
        embed = discord.Embed(
            title="Countdown Timer",
            description=f"Here is your countdown timer: {response.choices[0].message.content}",
            color=0x9C84EF,
        )
        await context.send(embed=embed)


async def setup(bot):
    await bot.add_cog(General(bot))
