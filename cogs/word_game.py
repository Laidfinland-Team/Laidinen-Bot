import sys, os; #sys.path.insert(0, os.path.join(os.getcwd(), ''))

from __init__ import *


class NameOfCommandGroupCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener() # This is a listener, like @bot.event
    async def on_ready(self):
        log.info("Help cog is ready")
        
    @commands.command() # This is a command, like @bot.command()
    async def ping(self, ctx):
        await ctx.send(f'Pong! {round(bot.latency * 1000)}ms')
        
async def setup(bot):
    await bot.add_cog(NameOfCommandGroupCog(bot))