import os
import discord
from discord.ext import commands
from api_client import ApiClient # type: ignore

TOKEN = os.getenv('DISCORD_TOKEN')
SERVER = os.getenv('DISCORD_SERVER')

api = ApiClient()
class MyBot(commands.Bot):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.my_server = None
        self.add_command(self.hello)
        self.add_command(self.get_player_details)
        self.add_command(self.board_game_link)
        

    async def on_ready(self):
        guild = discord.utils.get(self.guilds, name=SERVER)
        self.my_server = guild

        print(
            f'{self.user} has connected to the following server:\n'
            f'{guild.name} - id: {guild.id}'
        )

    async def on_command_error(self, ctx, error):
        if isinstance(error, commands.CommandNotFound):
            await ctx.send(f"Hey {ctx.author.name}, I cannot recognize the command **{ctx.invoked_with}**.")

    @commands.command(name='hello', help='Just say hi.')
    async def hello(ctx):
        await ctx.send(f"Hello {ctx.author.name}")

    @commands.command(name='player', help='Get details of a player given a handle.')
    async def get_player_details(ctx, handle):
        resp = api.get_player(handle)
        if resp == 404:
            msg = f"The player **{handle}** does not exist in the DB."
        else:
            attr_list = [f'{k}: {v}' for k, v in resp.items()]
            msg = f"Details for **{handle}**:\n"
            msg += '```' + '\n'.join(attr_list) + '```'
        await ctx.send(msg)

    @commands.command(name='bg', help='Get BGG link of a board game.')
    async def board_game_link(ctx, *args):
        name = ' '.join([arg for arg in args])
        resp = api.get_board_game_link(name)
        if resp == 404:
            msg = f"The game **{name}** does not exist in the DB."
        else:
            msg = f"Link for **{name}** is:\n"
            msg += resp
        await ctx.send(msg)




if __name__ == '__main__':
    bot = MyBot(command_prefix='!')
    bot.run(TOKEN)
