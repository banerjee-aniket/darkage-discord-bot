import discord
from discord.ext import commands
from discord import app_commands
import os
from datetime import datetime
from pathlib import Path

class General(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="ping", description="Check if the bot is alive")
    async def ping(self, interaction: discord.Interaction):
        await interaction.response.send_message("🏓 Pong! Bot is active and running fine!")

# THIS IS MANDATORY ↓↓↓
async def setup(bot):
    await bot.add_cog(General(bot))
