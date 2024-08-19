import bot
import json

if __name__ != "__main__":
    raise ImportError("This module should not be imported")

# Import and parse settings.json
with open('settings.json') as f:
    settings = json.load(f)

print("Settings are loaded")

# Start the bot
dc_bot = bot.DiscordBot(settings['token'])
dc_bot.run()