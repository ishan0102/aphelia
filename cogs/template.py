from discord.ext import commands
from discord.ext.commands import Context

from helpers import checks


class Template(commands.Cog, name="template"):
    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command(
        name="testcommand",
        description="This is a testing command that does nothing.",
    )
    # This will only allow owners of the bot to execute the command -> config.json
    @checks.is_owner()
    async def testcommand(self, context: Context):
        """
        This is a testing command that does nothing.

        :param context: The application command context.
        """
        pass


async def setup(bot):
    await bot.add_cog(Template(bot))
