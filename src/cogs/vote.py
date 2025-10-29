import discord
from discord.ext import commands
from discord import app_commands

class Vote(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # Slash command version of /vote
    @app_commands.command(name="vote", description="Support the DarkAge SMP server")
    async def vote(self, interaction: discord.Interaction):
        embed = discord.Embed(
            title="🗳️ Support DarkAge SMP",
            description=(
                "**Vote on TopG:** [Click Here](https://topg.org/minecraft-servers/server-123456)\n"
                "**Buy Me a Coffee:** [Support here](https://buymeacoffee.com/darkagesmp)"
            ),
            color=discord.Color.orange()
        )
        embed.set_footer(text="Every vote helps the server grow ❤️")
        await interaction.response.send_message(embed=embed)

# This function is required so main.py can load the cog properly
async def setup(bot):
    await bot.add_cog(Vote(bot))
