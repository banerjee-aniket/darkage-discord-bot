import discord
from discord.ext import commands
from discord import app_commands
import os
from datetime import datetime
from pathlib import Path
import requests
import aiohttp
import asyncio

class General(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="ping", description="Return bot latency")
    async def ping(self, interaction: discord.Interaction):
        latency = round(self.bot.latency * 1000)
        await interaction.response.send_message(f"🏓 Pong! Bot latency: {latency}ms")

    @app_commands.command(name="info", description="Read server info from info.md")
    async def info(self, interaction: discord.Interaction):
        try:
            info_path = Path("info.md")

            if not info_path.exists():
                await interaction.response.send_message("❌ info.md file not found.")
                return

            with open(info_path, 'r', encoding='utf-8') as file:
                content = file.read().strip()

            if not content:
                await interaction.response.send_message("ℹ️ No information available in info.md yet.")
            else:
                await interaction.response.send_message(f"**Server Information:**\n\n{content}")

        except Exception as e:
            await interaction.response.send_message("❌ Error reading info.md file.")

    @app_commands.command(name="news", description="Read latest server announcement from notice.md")
    async def news(self, interaction: discord.Interaction):
        try:
            notice_path = Path("notice.md")

            if not notice_path.exists():
                await interaction.response.send_message("❌ notice.md file not found.")
                return

            with open(notice_path, 'r', encoding='utf-8') as file:
                lines = file.readlines()

            # Find the most recent entry (last ## heading)
            latest_entry = []
            found_entry = False

            for line in reversed(lines):
                if line.strip().startswith('## ') and not found_entry:
                    latest_entry.insert(0, line)
                    found_entry = True
                elif found_entry and line.strip().startswith('## '):
                    break
                elif found_entry:
                    latest_entry.insert(0, line)

            if not latest_entry:
                await interaction.response.send_message("ℹ️ No announcements found in notice.md.")
            else:
                entry_text = ''.join(latest_entry).strip()
                await interaction.response.send_message(f"📢 **Latest Announcement:**\n\n{entry_text}")

        except Exception as e:
            await interaction.response.send_message("❌ Error reading notice.md file.")

    @app_commands.command(name="rules", description="Return the DarkAge SMP rulebook from rules.md")
    async def rules(self, interaction: discord.Interaction):
        try:
            rules_path = Path("rules.md")

            if not rules_path.exists():
                await interaction.response.send_message("❌ rules.md file not found.")
                return

            with open(rules_path, 'r', encoding='utf-8') as file:
                content = file.read().strip()

            if not content:
                await interaction.response.send_message("ℹ️ No rules available in rules.md yet.")
            else:
                await interaction.response.send_message(f"📖 **DarkAge SMP Rules:**\n\n{content}")

        except Exception as e:
            await interaction.response.send_message("❌ Error reading rules.md file.")

    @app_commands.command(name="status", description="Check SMP server status using Minecraft API")
    async def status(self, interaction: discord.Interaction):
        try:
            await interaction.response.defer()

            # Using default Minecraft status API (example with mc.hypixel.net - replace with actual SMP server)
            server_ip = "mc.hypixel.net"  # Replace with actual SMP server IP
            api_url = f"https://api.mcsrvstat.us/3/{server_ip}"

            async with aiohttp.ClientSession() as session:
                async with session.get(api_url) as response:
                    if response.status == 200:
                        data = await response.json()

                        if data.get('online'):
                            version = data.get('version', 'Unknown')
                            players = data.get('players', {})
                            online_count = players.get('online', 0)
                            max_count = players.get('max', 0)

                            embed = discord.Embed(
                                title="🟢 Server Status: Online",
                                color=discord.Color.green()
                            )
                            embed.add_field(name="Version", value=version, inline=True)
                            embed.add_field(name="Players", value=f"{online_count}/{max_count}", inline=True)
                            embed.set_footer(text=f"Server: {server_ip}")
                        else:
                            embed = discord.Embed(
                                title="🔴 Server Status: Offline",
                                color=discord.Color.red()
                            )
                            embed.description = "The SMP server is currently offline."
                            embed.set_footer(text=f"Server: {server_ip}")
                    else:
                        embed = discord.Embed(
                            title="❌ Status Check Failed",
                            color=discord.Color.red()
                        )
                        embed.description = "Unable to retrieve server status."

            await interaction.followup.send(embed=embed)

        except Exception as e:
            await interaction.followup.send("❌ Error checking server status.")

    @app_commands.command(name="players", description="Return the full SMP player list from players.md")
    async def players(self, interaction: discord.Interaction):
        try:
            players_path = Path("players.md")

            if not players_path.exists():
                await interaction.response.send_message("❌ No registered players yet.")
                return

            with open(players_path, 'r', encoding='utf-8') as file:
                content = file.read().strip()

            if not content:
                await interaction.response.send_message("ℹ️ No registered players yet.")
            else:
                await interaction.response.send_message(f"👥 **SMP Player Roster:**\n\n{content}")

        except Exception as e:
            await interaction.response.send_message("❌ Error reading players.md file.")

    @app_commands.command(name="player", description="Manage player roster")
    @app_commands.describe(action="Action to perform", username="Minecraft username")
    async def player(self, interaction: discord.Interaction, action: str, username: str):
        if action.lower() != "add":
            await interaction.response.send_message("❌ Invalid action. Use `/player add <username>`")
            return

        try:
            players_path = Path("players.md")

            # Read existing players
            existing_players = []
            if players_path.exists():
                with open(players_path, 'r', encoding='utf-8') as file:
                    content = file.read()
                    # Extract player names (simplified - assumes format like "- PlayerName")
                    for line in content.split('\n'):
                        if line.strip().startswith('- '):
                            player_name = line.strip()[2:].strip()
                            if player_name:
                                existing_players.append(player_name.lower())

            # Check for duplicates
            if username.lower() in existing_players:
                await interaction.response.send_message(f"⚠️ Player '{username}' is already registered.")
                return

            # Add new player
            with open(players_path, 'a', encoding='utf-8') as file:
                file.write(f"- {username}\n")

            await interaction.response.send_message(f"✅ Successfully added '{username}' to the player roster!")

        except Exception as e:
            await interaction.response.send_message("❌ Error adding player to roster.")

# THIS IS MANDATORY ↓↓↓
async def setup(bot):
    await bot.add_cog(General(bot))
