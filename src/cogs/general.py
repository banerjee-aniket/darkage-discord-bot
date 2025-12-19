import discord
from discord.ext import commands
from discord import app_commands, ui
from src.utils.config_manager import config_manager
import logging

logger = logging.getLogger(__name__)

class General(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    def is_enabled(self, command_name: str) -> bool:
        return config_manager.get(f"commands.{command_name}", True)

    @app_commands.command(name="ping", description="Return bot latency")
    async def ping(self, interaction: discord.Interaction):
        if not self.is_enabled("ping"):
            await interaction.response.send_message("This command is disabled.", ephemeral=True)
            return
        
        latency = round(self.bot.latency * 1000)
        await interaction.response.send_message(f"🏓 Pong! Latency: {latency}ms")

    @app_commands.command(name="website", description="Display server website URL")
    async def website(self, interaction: discord.Interaction):
        if not self.is_enabled("website"):
            await interaction.response.send_message("This command is disabled.", ephemeral=True)
            return
        
        url = config_manager.get("links.website")
        await interaction.response.send_message(f"🌐 Website: {url}")

    @app_commands.command(name="store", description="Show donation/store link")
    async def store(self, interaction: discord.Interaction):
        if not self.is_enabled("store"):
            await interaction.response.send_message("This command is disabled.", ephemeral=True)
            return
        
        url = config_manager.get("links.store")
        await interaction.response.send_message(f"🛒 Store: {url}")

    @app_commands.command(name="rules", description="Output server rules text")
    async def rules(self, interaction: discord.Interaction):
        if not self.is_enabled("rules"):
            await interaction.response.send_message("This command is disabled.", ephemeral=True)
            return
        
        rules_text = config_manager.get("rules")
        embed = discord.Embed(title="📜 Server Rules", description=rules_text, color=discord.Color.blue())
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="vote", description="Render interactive buttons for vote links")
    async def vote(self, interaction: discord.Interaction):
        if not self.is_enabled("vote"):
            await interaction.response.send_message("This command is disabled.", ephemeral=True)
            return
        
        vote_links = config_manager.get("links.vote", [])
        if not vote_links:
            await interaction.response.send_message("No vote links configured.", ephemeral=True)
            return

        view = ui.View()
        for i, link in enumerate(vote_links):
            label = f"Vote Link {i+1}"
            view.add_item(ui.Button(label=label, url=link, style=discord.ButtonStyle.link))

        embed = discord.Embed(
            title="🗳️ Vote for DarkAge SMP",
            description="Support the server by voting! Click the buttons below.",
            color=discord.Color.orange()
        )
        await interaction.response.send_message(embed=embed, view=view)

    @app_commands.command(name="help", description="List all enabled commands")
    async def help(self, interaction: discord.Interaction):
        if not self.is_enabled("help"):
            await interaction.response.send_message("This command is disabled.", ephemeral=True)
            return
        
        embed = discord.Embed(title="🤖 Bot Commands", color=discord.Color.gold())
        
        # Gather commands from all cogs
        for cog_name, cog in self.bot.cogs.items():
            commands_list = []
            # App commands (Slash commands)
            for cmd in cog.walk_app_commands():
                if config_manager.get(f"commands.{cmd.name}", True):
                    commands_list.append(f"/{cmd.name} - {cmd.description}")
            
            if commands_list:
                embed.add_field(name=cog_name, value="\n".join(commands_list), inline=False)
        
        # Add reload command (in tree but not in cog, or check global commands)
        other_commands = []
        for cmd in self.bot.tree.get_commands():
            # Check if command belongs to a cog
            if cmd.binding is None: # Not in a cog
                 if config_manager.get(f"commands.{cmd.name}", True):
                    other_commands.append(f"/{cmd.name} - {cmd.description}")

        if other_commands:
            embed.add_field(name="Other", value="\n".join(other_commands), inline=False)

        await interaction.response.send_message(embed=embed)

async def setup(bot):
    await bot.add_cog(General(bot))
