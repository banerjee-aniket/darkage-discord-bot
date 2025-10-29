import discord
from discord.ext import commands
import aiohttp

SERVER_IP = "darkagesmp.enderman.cloud"
PORT = 31938
API_URL = f"https://api.mcsrvstat.us/bedrock/3/darkagesmp.enderman.cloud:31938"

class MinecraftStatus(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="status")
    async def status(self, ctx):
        async with aiohttp.ClientSession() as session:
            async with session.get(API_URL) as response:
                data = await response.json()

                if not data.get("online"):
                    await ctx.send("❌ The server is currently offline.")
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
                embed.set_footer(text="Powered by DarkAge SMP API")
                await ctx.send(embed=embed)

    @commands.command(name="ip")
    async def ip(self, ctx):
        await ctx.send(f"🧭 Server IP: `{SERVER_IP}:{PORT}`")

    @commands.command(name="motd")
    async def motd(self, ctx):
        async with aiohttp.ClientSession() as session:
            async with session.get(API_URL) as response:
                data = await response.json()
                motd = data.get("motd", {}).get("clean", ["No MOTD"])[0]
                await ctx.send(f"📝 MOTD: {motd}")

    @commands.command(name="players")
    async def players(self, ctx):
        async with aiohttp.ClientSession() as session:
            async with session.get(API_URL) as response:
                data = await response.json()
                if not data.get("online"):
                    await ctx.send("❌ Server is offline, can't fetch players.")
                    return
                player_list = data["players"].get("list", [])
                if not player_list:
                    await ctx.send("👻 No players are currently online.")
                    return
                await ctx.send("🧑‍🚀 Online Players:\n" + "\n".join(player_list))

# ✅ Required for Discord.py 2.x
async def setup(bot):
    await bot.add_cog(MinecraftStatus(bot))
