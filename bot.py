import discord
import shell


class DiscordBot:
    def __init__(self, token):
        intents = discord.Intents.default()

        self.token = token
        self.client = discord.Client(intents=intents)

        @self.client.event
        async def on_ready():
            print(f'Connected to discord as `{self.client.user}`')
            await shell.Shell(self.client).run()
            print("Exiting...")
            await self.client.close()

    def run(self):
        self.client.run(self.token)
