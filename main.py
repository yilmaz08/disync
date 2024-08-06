import argparse
import discord
import json
import yaml
import base64
import secrets
import string

if __name__ != "__main__":
    raise ImportError("This module should not be imported")

# Import and parse settings.json
with open('settings.json') as f:
    settings = json.load(f)

print("Settings are loaded")

# Parse arguments
parser = argparse.ArgumentParser()
parser.add_argument('action', type=str, help='Action to perform', choices=["ls", "tree", "touch", "mkdir", "rm", "rmdir", "write", "download"])
parser.add_argument('file', type=str, help='File to perform action on')
parser.add_argument('--local', type=str, help='Local path to use for download and upload actions', default="")
args = parser.parse_args()

print("Arguments are parsed")

# Start Discord bot
intents = discord.Intents.default()
client = discord.Client(intents=intents)

@client.event
async def on_ready():
    print(f'\"{client.user}\" has connected to Discord!')
    # Find the guild
    guild = None
    for _guild in client.guilds:
        if _guild.id == settings["guild"]:
            print(f"Found the guild: {_guild.name}")
            guild = _guild
            break
    if guild is None:
        print("Guild not found")
        await client.close()
        return
    # Find the root channel
    root_channel = None
    for _channel in guild.text_channels:
        if _channel.id == settings["root"]:
            print(f"Found the root channel: {_channel.name}")
            root_channel = _channel
            break
    if root_channel is None:
        print("Root channel not found")
        await client.close()
        return
    # Perform action
    print(f"Action to perform: {args.action}")

    await client.close()
    return

client.run(settings["token"])
