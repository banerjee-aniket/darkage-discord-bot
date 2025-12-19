import discord
from discord.ext import commands
from dotenv import load_dotenv
import os
import asyncio
import logging
from src.utils.config_manager import config_manager
import threading
import uvicorn
from src.dashboard.app import app as dashboard_app

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("bot.log", encoding="utf-8"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("Main")

# Load environment variables
load_dotenv()

class DarkageBot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.all()
        super().__init__(command_prefix="!", intents=intents)

    async def setup_hook(self):
        # Load cogs
        cogs_dir = os.path.join(os.path.dirname(__file__), "src", "cogs")
        if os.path.exists(cogs_dir):
            for filename in os.listdir(cogs_dir):
                if filename.endswith(".py") and filename != "__init__.py":
                    try:
                        await self.load_extension(f"src.cogs.{filename[:-3]}")
                        logger.info(f"✅ Loaded cog: {filename}")
                    except Exception as e:
                        logger.error(f"❌ Failed to load cog {filename}: {e}")
        else:
            logger.warning(f"Cogs directory not found at {cogs_dir}")

        # Sync commands
        await self.tree.sync()
        logger.info("✅ Slash commands synced successfully!")

bot = DarkageBot()

@bot.event
async def on_ready():
    logger.info(f"Logged in as {bot.user} (ID: {bot.user.id})")
    # Set status
    ip = config_manager.get("minecraft.ip", "Minecraft Server")
    await bot.change_presence(activity=discord.Game(name=f"Playing on {ip}"))

@bot.tree.command(name="reload", description="Reloads the configuration (Owner only)")
async def reload(interaction: discord.Interaction):
    # Check if user is owner
    if not await bot.is_owner(interaction.user):
        await interaction.response.send_message("❌ You are not authorized to use this command.", ephemeral=True)
        return

    try:
        config_manager.reload()
        await interaction.response.send_message("✅ Configuration reloaded successfully!", ephemeral=True)
        logger.info(f"Config reloaded by {interaction.user}")
    except Exception as e:
        await interaction.response.send_message(f"❌ Failed to reload config: {e}", ephemeral=True)
        logger.error(f"Failed to reload config: {e}")

def run_dashboard():
    port = int(os.getenv("PORT", 8080))
    logger.info(f"Starting dashboard on port {port}")
    # Disable uvicorn access logs to keep console clean, or keep them for debug
    uvicorn.run(dashboard_app, host="0.0.0.0", port=port, log_level="info")

async def main():
    token = os.getenv("DISCORD_TOKEN")
    if not token:
        logger.critical("DISCORD_TOKEN not found in environment variables!")
        return

    # Start Dashboard in a separate thread
    dashboard_thread = threading.Thread(target=run_dashboard, daemon=True)
    dashboard_thread.start()
    
    async with bot:
        await bot.start(token)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass
