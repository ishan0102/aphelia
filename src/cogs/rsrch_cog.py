import io
import re
import sys
from discord.ext import commands
from rsrch import upload


class RsrchCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.bot.add_listener(self.on_message, "on_message")

    async def on_message(self, message):
        if message.author == self.bot.user or message.channel.name != "rsrch":
            return

        # Redirect stdout to a StringIO object
        original_stdout = sys.stdout
        sys.stdout = captured_stdout = io.StringIO()

        # Use regular expressions to search for URLs in the message content
        urls = re.findall("(?P<url>https?://[^\s]+)", message.content)

        # Push the URLs to push_papers
        upload(urls)

        # Reset stdout to the original value
        sys.stdout = original_stdout

        # Get the captured output and send it to the channel
        output = captured_stdout.getvalue()
        if output:
            await message.channel.send(f"```\n{output}\n```")
        else:
            await message.channel.send("No output was captured.")

        await self.bot.process_commands(message)
