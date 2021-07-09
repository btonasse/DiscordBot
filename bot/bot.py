import os
import discord
from discord.ext import commands
from api_client import ApiClient # type: ignore
import json

TOKEN = os.getenv('DISCORD_TOKEN')
SERVER = os.getenv('DISCORD_SERVER')

class MyBot(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.api = ApiClient()
        self.my_server = None

    @commands.Cog.listener()
    async def on_ready(self):
        guild = discord.utils.get(self.bot.guilds, name=SERVER)
        self.my_server = guild

        print(
            f'{self.bot.user} has connected to the following server:\n'
            f'{guild.name} - id: {guild.id}'
        )
    
    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        if isinstance(error, commands.CommandNotFound):
            await ctx.send(f"Hey {ctx.author.name}, I cannot recognize the command **{ctx.invoked_with}**.")

    @commands.command(name='hello', help='Just say hi.')
    async def hello(self, ctx):
        await ctx.send(f"Hello {ctx.author.name}")

    @commands.command(name='player', help='Get details of a player given a handle.')
    async def get_player_details(self, ctx, handle):
        resp = self.api.get_player(handle)
        if resp == 404:
            msg = f"The player **{handle}** does not exist in the DB."
        else:
            msg = f"Details for **{handle}**:\n"
            msg += self.to_comment_block(resp)
        await ctx.send(msg)

    @commands.command(name='bg', help='Get BGG link of a board game.')
    async def board_game_link(self, ctx, *args):
        name = ' '.join([arg for arg in args])
        resp = self.api.get_board_game_link(name)
        if resp == 404:
            msg = f"The game **{name}** does not exist in the DB."
        else:
            msg = f"Link for **{name}** is:\n"
            msg += resp
        await ctx.send(msg)

    @commands.command(name='new_match', help='Create a match with results per player.')
    async def create_match(self, ctx, game, date, *results):
        results_list = []
        for res in results:
            as_list = res.split(' ')
            new_dict = {'player': as_list[0], 'points': as_list[1]}
            results_list.append(new_dict)
        data_to_post = {
            'game': game,
            'date': date,
            'results': results_list
        }
        resp = self.api.create_match(data=data_to_post)
        msg = self.to_comment_block(resp)
        await ctx.send(msg)

    def to_comment_block(self, orig_dict):
        '''
        Takes a an object from a request response and turns it into a comment block
        '''
        indented_str = json.dumps(orig_dict, indent=2)
        as_list = indented_str.split('\n')
        new_lines = []
        for line in as_list:
            if line[-1] in [',', '{', '}', '[', ']']:
                new_line = line[:-1]
                if len(new_line.strip()) >= 2: # Only adds lines back that have actual content
                    new_lines.append(new_line)
                if len(new_line.strip()) == 0:
                    new_lines.append('') # Get separation between nested records
            else:
                new_lines.append(line)
        new_string = '\n'.join(new_lines).strip()
        new_string = new_string.replace('"', '') # Get rid of quotes
        as_comment = '```' + new_string + '```'
        return as_comment

bot = commands.Bot(command_prefix='!')
bot.add_cog(MyBot(bot))

if __name__ == '__main__':
    bot.run(TOKEN)

"""
api = ApiClient()
class MyBot(commands.Bot):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.my_server = None
        self.add_command(self.hello)
        self.add_command(self.get_player_details)
        self.add_command(self.board_game_link)
        self.add_command(self.create_match)
        

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
            msg = f"Details for **{handle}**:\n"
            msg += to_comment_block(resp)
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

    @commands.command(name='new_match', help='Create a match with results per player.')
    async def create_match(ctx, game, date, *results):
        results_list = []
        for res in results:
            as_list = res.split(' ')
            new_dict = {'player': as_list[0], 'points': as_list[1]}
            results_list.append(new_dict)
        data_to_post = {
            'game': game,
            'date': date,
            'results': results_list
        }
        resp = api.create_match(data=data_to_post)
        msg = to_comment_block(resp)
        await ctx.send(msg)
            

def to_comment_block(orig_dict):
    '''
    Takes a an object from a request response and turns it into a comment block
    '''
    indented_str = json.dumps(orig_dict, indent=2)
    as_list = indented_str.split('\n')
    new_lines = []
    for line in as_list:
        if line[-1] in [',', '{', '}', '[', ']']:
            new_line = line[:-1]
            if len(new_line.strip()) >= 2: # Only adds lines back that have actual content
                new_lines.append(new_line)
            if len(new_line.strip()) == 0:
                new_lines.append('') # Get separation between nested records
        else:
            new_lines.append(line)
    new_string = '\n'.join(new_lines).strip()
    new_string = new_string.replace('"', '') # Get rid of quotes
    as_comment = '```' + new_string + '```'
    return as_comment


if __name__ == '__main__':
    bot = MyBot(command_prefix='!')
    bot.run(TOKEN)
"""