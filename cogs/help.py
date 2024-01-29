import sys, os; #sys.path.insert(0, os.path.join(os.getcwd(), ''))

from __init__ import *



class HelpCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        info("Help cog is ready")
        
    @commands.command()
    async def ping(self, ctx):
        await ctx.send(f'Pong! {round(bot.latency * 1000)}ms')
    """ @commands.command(name='hel1p', aliases=['h'])
    async def help(self, ctx):
        await ctx.send(f'**{ctx.author.name}**, check your direct messages!')
        await ctx.author.send(f'**{ctx.author.name}**, check your direct messages!')
        embed = discord.Embed(title='Help on BOT', description='Some useful commands')
        embed.add_field(name='{}test'.format(PREFIX), value='Returns the argument you give')
        await ctx.author.send(embed=embed) """
        
async def setup(bot):
    await bot.add_cog(HelpCog(bot))