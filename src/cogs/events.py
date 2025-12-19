import discord
from discord.ext import commands
import logging
from src.utils.config_manager import config_manager

logger = logging.getLogger(__name__)

class Events(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_member_join(self, member: discord.Member):
        if not config_manager.get("welcome.enabled", False):
            return

        channel_id = config_manager.get("welcome.channel_id")
        if not channel_id:
            # Only log warning once or if really needed, to avoid spam if misconfigured
            return

        channel = self.bot.get_channel(int(channel_id))
        if not channel:
            logger.warning(f"Welcome channel ID {channel_id} not found.")
            return

        message_template = config_manager.get("welcome.message", "Welcome {user}!")
        message = message_template.replace("{user}", member.mention)

        try:
            await channel.send(message)
            logger.info(f"Sent welcome message for {member} in {channel.name}")
        except discord.Forbidden:
            logger.error(f"Missing permissions to send welcome message in {channel.name}")
        except Exception as e:
            logger.error(f"Error sending welcome message: {e}")

async def setup(bot):
    await bot.add_cog(Events(bot))
