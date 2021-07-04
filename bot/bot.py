import os
import discord
from discord.ext import commands

TOKEN = os.getenv('DISCORD_TOKEN')
SERVER = os.getenv('DISCORD_SERVER')


class MyBot(commands.Bot):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.my_server = None
        self.add_command(self.hello)
        

    async def on_ready(self):
        guild = discord.utils.get(self.guilds, name=SERVER)
        self.my_server = guild

        print(
            f'{self.user} has connected to the following server:\n'
            f'{guild.name} - id: {guild.id}'
        )

    @commands.command(name='hello', help='Just say hi.')
    async def hello(ctx):
        await ctx.send(f"Hello {ctx.author.name}")


if __name__ == '__main__':
    bot = MyBot(command_prefix='!')
    bot.run(TOKEN)
