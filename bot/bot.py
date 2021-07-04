import os
import discord

TOKEN = os.getenv('DISCORD_TOKEN')
SERVER = os.getenv('DISCORD_SERVER')

class MyClient(discord.Client):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.my_guild = None
    
    async def on_ready(self):
        guild = discord.utils.get(self.guilds, name=SERVER)
        self.my_server = guild

        print(
            f'{self.user} has connected to the following server:\n'
            f'{guild.name} - id: {guild.id}'
        )


client = MyClient()
client.run(TOKEN)