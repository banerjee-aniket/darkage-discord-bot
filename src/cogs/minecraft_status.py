import discord
from discord.ext import commands
from discord import app_commands
import aiohttp
import logging
from src.utils.config_manager import config_manager

logger = logging.getLogger(__name__)

class MinecraftStatus(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    def is_enabled(self, command_name: str) -> bool:
        return config_manager.get(f"commands.{command_name}", True)

    async def get_server_data(self):
        ip = config_manager.get("minecraft.ip")
        port = config_manager.get("minecraft.port")
        # Assuming Bedrock based on previous code. If Java, URL differs. 
        # Previous code used bedrock/3/, so I stick with it.
        url = f"https://api.mcsrvstat.us/bedrock/3/{ip}:{port}"
        
        async with aiohttp.ClientSession() as session:
            try:
                async with session.get(url, timeout=5) as response:
                    if response.status == 200:
                        return await response.json()
            except Exception as e:
                logger.error(f"Failed to fetch server data: {e}")
        return None

    @app_commands.command(name="status", description="Show server status (online/offline), player count, and latency")
    async def status(self, interaction: discord.Interaction):
        if not self.is_enabled("status"):
            await interaction.response.send_message("This command is disabled.", ephemeral=True)
            return

        await interaction.response.defer()
        data = await self.get_server_data()

        if not data or not data.get("online"):
            await interaction.followup.send("❌ The server is currently offline.")
            return

        players = data["players"].get("online", 0)
        max_players = data["players"].get("max", 0)
        version = data.get("version", "Unknown")
        motd = data.get("motd", {}).get("clean", ["No MOTD"])[0]
        
        embed = discord.Embed(
            title="🌍 DarkAge SMP Status",
            color=discord.Color.green()
        )
        embed.add_field(name="Status", value="✅ Online", inline=False)
        embed.add_field(name="Players", value=f"{players}/{max_players}", inline=True)
        embed.add_field(name="Version", value=version, inline=True)
        embed.add_field(name="MOTD", value=motd, inline=False)
        
        ip = config_manager.get("minecraft.ip")
        port = config_manager.get("minecraft.port")
        embed.set_footer(text=f"IP: {ip}:{port}")
        
        await interaction.followup.send(embed=embed)

    @app_commands.command(name="ip", description="Display Minecraft server IP + port")
    async def ip(self, interaction: discord.Interaction):
        if not self.is_enabled("ip"):
            await interaction.response.send_message("This command is disabled.", ephemeral=True)
            return
            
        ip = config_manager.get("minecraft.ip")
        port = config_manager.get("minecraft.port")
        await interaction.response.send_message(f"🧭 Server IP: `{ip}:{port}`")

    @app_commands.command(name="players", description="Display current/max player count")
    async def players(self, interaction: discord.Interaction):
        if not self.is_enabled("players"):
            await interaction.response.send_message("This command is disabled.", ephemeral=True)
            return

        await interaction.response.defer()
        data = await self.get_server_data()

        if not data or not data.get("online"):
            await interaction.followup.send("❌ Server is offline.")
            return

        players = data["players"].get("online", 0)
        max_players = data["players"].get("max", 0)
        player_list = data["players"].get("list", [])

        msg = f"🧑‍🚀 **Players Online:** {players}/{max_players}"
        if player_list:
            msg += "\n" + "\n".join([f"• {p}" for p in player_list])
        
        await interaction.followup.send(msg)

    @app_commands.command(name="version", description="Output server version information")
    async def version(self, interaction: discord.Interaction):
        if not self.is_enabled("version"):
            await interaction.response.send_message("This command is disabled.", ephemeral=True)
            return

        await interaction.response.defer()
        data = await self.get_server_data()

        if not data or not data.get("online"):
            await interaction.followup.send("❌ Server is offline.")
            return

        version = data.get("version", "Unknown")
        await interaction.followup.send(f"ℹ️ Server Version: **{version}**")

async def setup(bot):
    await bot.add_cog(MinecraftStatus(bot))
