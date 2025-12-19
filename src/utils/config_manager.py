import json
import os
import asyncio
import aiofiles
from typing import Dict, Any, Union
import logging

logger = logging.getLogger(__name__)

CONFIG_PATH = os.path.abspath("config.json")

DEFAULT_CONFIG = {
    "minecraft": {
        "ip": "darkagesmp.enderman.cloud",
        "port": 31938
    },
    "links": {
        "website": "https://darkagesmp.com",
        "store": "https://store.darkagesmp.com",
        "vote": [
            "https://topg.org/minecraft-servers/server-123456",
            "https://minecraft-server-list.com/server/123456"
        ]
    },
    "rules": "1. No griefing\n2. No hacking\n3. Be respectful",
    "welcome": {
        "enabled": True,
        "channel_id": 0,
        "message": "Welcome {user} to DarkAge SMP!"
    },
    "commands": {
        "ip": True,
        "status": True,
        "players": True,
        "version": True,
        "ping": True,
        "vote": True,
        "website": True,
        "store": True,
        "rules": True,
        "help": True,
        "motd": True
    }
}

class ConfigManager:
    def __init__(self, path: str = CONFIG_PATH):
        self.path = path
        self.config = {}
        self._lock = asyncio.Lock()
        self.load_config()

    def load_config(self):
        if not os.path.exists(self.path):
            logger.info("Config file not found. Creating default config.")
            self.config = DEFAULT_CONFIG.copy()
            self.save_config_sync()
        else:
            try:
                with open(self.path, "r", encoding="utf-8") as f:
                    self.config = json.load(f)
                # Validate and merge defaults
                self._validate_schema()
            except (json.JSONDecodeError, IOError) as e:
                logger.error(f"Error loading config: {e}. Using default.")
                self.config = DEFAULT_CONFIG.copy()
                # Attempt to save the default if the file is corrupted
                self.save_config_sync()

    def _validate_schema(self):
        """Recursively merge defaults for missing keys."""
        changed = False
        
        def recursive_merge(default_dict, target_dict):
            nonlocal changed
            for key, value in default_dict.items():
                if key not in target_dict:
                    target_dict[key] = value
                    changed = True
                elif isinstance(value, dict) and isinstance(target_dict[key], dict):
                    recursive_merge(value, target_dict[key])
        
        recursive_merge(DEFAULT_CONFIG, self.config)
        
        if changed:
            logger.info("Config schema updated with missing keys.")
            self.save_config_sync()

    def save_config_sync(self):
        """Atomic write (synchronous)"""
        temp_path = self.path + ".tmp"
        try:
            with open(temp_path, "w", encoding="utf-8") as f:
                json.dump(self.config, f, indent=4)
            os.replace(temp_path, self.path)
            logger.info("Config saved successfully.")
        except Exception as e:
            logger.error(f"Failed to save config: {e}")

    async def save_config(self):
        """Atomic write (asynchronous)"""
        async with self._lock:
            temp_path = self.path + ".tmp"
            try:
                async with aiofiles.open(temp_path, "w", encoding="utf-8") as f:
                    await f.write(json.dumps(self.config, indent=4))
                os.replace(temp_path, self.path)
                logger.info("Config saved successfully (async).")
            except Exception as e:
                logger.error(f"Failed to save config async: {e}")

    def get(self, key: str, default: Any = None) -> Any:
        """Get a value using dot notation (e.g., 'minecraft.ip')"""
        keys = key.split(".")
        val = self.config
        for k in keys:
            if isinstance(val, dict):
                val = val.get(k)
            else:
                return default
        return val if val is not None else default

    async def set(self, key: str, value: Any):
        """Set a value using dot notation and save"""
        keys = key.split(".")
        target = self.config
        for k in keys[:-1]:
            target = target.setdefault(k, {})
        target[keys[-1]] = value
        await self.save_config()

    def reload(self):
        """Reload configuration from disk"""
        self.load_config()

config_manager = ConfigManager()
