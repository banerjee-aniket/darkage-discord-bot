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

    @app_commands.command(name="info", description="Display server information")
    async def info(self, interaction: discord.Interaction):
        try:
            info_path = Path("info.md")

            if not info_path.exists():
                embed = discord.Embed(
                    title="Server Information",
                    description="Information file not found. Please contact server admin.",
                    color=discord.Color.red()
                )
                embed.set_footer(text="Error: File not found")
                await interaction.response.send_message(embed=embed)
                return

            try:
                with open(info_path, 'r', encoding='utf-8') as file:
                    content = file.read().strip()

                if not content or len(content) < 5:
                    description = "No information available yet. Check back later!"
                else:
                    description = content

                embed = discord.Embed(
                    title="Server Information",
                    description=description,
                    color=discord.Color.blue()  # #3498db
                )
                embed.set_footer(text=f"Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
                await interaction.response.send_message(embed=embed)

            except PermissionError:
                embed = discord.Embed(
                    title="Server Information",
                    description="Unable to access information file. Please check file permissions.",
                    color=discord.Color.red()
                )
                embed.set_footer(text="Error: Permission denied")
                await interaction.response.send_message(embed=embed)

            except UnicodeDecodeError:
                embed = discord.Embed(
                    title="Server Information",
                    description="Information file format error. Please contact admin.",
                    color=discord.Color.red()
                )
                embed.set_footer(text="Error: File format")
                await interaction.response.send_message(embed=embed)

        except Exception as e:
            embed = discord.Embed(
                title="Server Information",
                description="Error reading information. Please try again later.",
                color=discord.Color.red()
            )
            embed.set_footer(text="Error: Unknown")
            await interaction.response.send_message(embed=embed)

    @app_commands.command(name="help", description="Show all available commands")
    async def help(self, interaction: discord.Interaction):
        embed = discord.Embed(
            title="Bot Commands",
            description="Here are all the available slash commands:",
            color=discord.Color.green()  # #2ecc71
        )

        commands_list = [
            ("/ping", "Check if the bot is alive"),
            ("/info", "Display server information"),
            ("/help", "Show all available commands"),
            ("/server", "Show server information"),
            ("/user", "Show your user information"),
            ("/about", "Show bot information")
        ]

        for command, description in commands_list:
            embed.add_field(name=command, value=description, inline=False)

        embed.set_footer(text="Use /command_name to execute")
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="server", description="Show server information")
    async def server(self, interaction: discord.Interaction):
        if not interaction.guild:
            embed = discord.Embed(
                title="Server Information",
                description="This command can only be used in a server.",
                color=discord.Color.red()
            )
            await interaction.response.send_message(embed=embed)
            return

        guild = interaction.guild
        embed = discord.Embed(
            title=guild.name,
            color=discord.Color.purple()  # #9b59b6
        )

        embed.add_field(name="Owner", value=f"<@{guild.owner_id}>", inline=True)
        embed.add_field(name="Members", value=str(guild.member_count), inline=True)
        embed.add_field(name="Created", value=guild.created_at.strftime("%Y-%m-%d"), inline=True)

        boost_level = guild.premium_tier
        embed.add_field(name="Boost Level", value=f"Level {boost_level}", inline=True)
        embed.add_field(name="Emojis", value=str(len(guild.emojis)), inline=True)

        if guild.icon:
            embed.set_thumbnail(url=guild.icon.url)

        embed.set_footer(text=f"Server ID: {guild.id}")
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="user", description="Show your user information")
    @app_commands.describe(target="Select a user to view their info (optional)")
    async def user(self, interaction: discord.Interaction, target: discord.Member = None):
        user = target or interaction.user

        embed = discord.Embed(
            title=user.display_name,
            color=discord.Color.orange()  # #e67e22
        )

        embed.add_field(name="Username", value=f"{user.name}#{user.discriminator}", inline=True)

        if interaction.guild:
            member = interaction.guild.get_member(user.id)
            if member:
                embed.add_field(name="Joined Server", value=member.joined_at.strftime("%Y-%m-%d"), inline=True)
                if member.top_role and member.top_role.name != "@everyone":
                    embed.add_field(name="Top Role", value=member.top_role.mention, inline=True)

        embed.add_field(name="Account Created", value=user.created_at.strftime("%Y-%m-%d"), inline=True)

        if user.avatar:
            embed.set_thumbnail(url=user.avatar.url)

        embed.set_footer(text=f"User ID: {user.id}")
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="about", description="Show bot information")
    async def about(self, interaction: discord.Interaction):
        embed = discord.Embed(
            title="Darkage Bot",
            description="A multi-purpose Discord bot for server management and entertainment.",
            color=discord.Color.dark_blue()  # #2c3e50
        )

        embed.add_field(name="Version", value="1.0.0", inline=True)
        embed.add_field(name="Creator", value="Server Administration", inline=True)
        embed.add_field(name="Servers", value=str(len(self.bot.guilds)), inline=True)

        uptime = datetime.now() - self.bot.user.created_at.replace(tzinfo=None)
        days = uptime.days
        hours, remainder = divmod(uptime.seconds, 3600)
        embed.add_field(name="Uptime", value=f"{days}d {hours}h", inline=True)

        embed.set_thumbnail(url=self.bot.user.avatar.url if self.bot.user.avatar else None)
        embed.set_footer(text="Made with discord.py")
        await interaction.response.send_message(embed=embed)

# THIS IS MANDATORY ↓↓↓
async def setup(bot):
    await bot.add_cog(General(bot))
