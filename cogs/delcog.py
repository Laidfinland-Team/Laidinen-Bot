import sys, os; #sys.path.insert(0, os.path.join(os.getcwd(), ''))

from __init__ import *


class DelCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener() # This is a listener, like @bot.event
    async def on_ready(self):
        info("DelCog cog is ready")
        
    @commands.command(name='delete_this', aliases=['delthis', 'del'])
    @commands.has_role(1156880728953454592)
    async def delete_this(self, ctx: Ctx, amount: str):
        await ctx.send('Да да, я ключевое слово!')
        
async def setup(bot):
    await bot.add_cog(DelCog(bot))