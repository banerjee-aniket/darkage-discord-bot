import discord
from discord.ext import commands
from dotenv import load_dotenv
import os
import asyncio

# Load environment variables
load_dotenv()

class DarkageBot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.all()
        super().__init__(command_prefix="!", intents=intents)

    async def setup_hook(self):
        for filename in os.listdir("./src/cogs"):
            # ✅ Skip __init__.py so it doesn’t throw NoEntryPointError
            if filename.endswith(".py") and filename != "__init__.py":
                await self.load_extension(f"src.cogs.{filename[:-3]}")
                print(f"✅ Loaded cog: {filename}")
        await self.tree.sync()
        print("✅ Slash commands synced successfully!")

bot = DarkageBot()

@bot.event
async def on_ready():
    print(f"🤖 Logged in as {bot.user}")

async def main():
    async with bot:
        await bot.start(os.getenv("DISCORD_TOKEN"))

if __name__ == "__main__":
    asyncio.run(main())
