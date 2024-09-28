
from __init__ import *
import random


kam_list = []

class kamikazeCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener() # This is a listener, like @bot.event
    async def on_ready(self):
        info("Kamikaze cog is ready")
        
    
    @commands.command() # This is a command, like @bot.command()
    @disabled()
    async def kamikaze(self, ctx: Ctx, member: discord.Member):
        mute = 1 #random.randint(1, 3)
        try:
            await ctx.author.timeout(datetime.now(jerusalem_tz) + timedelta(minutes=mute))
            info(f"{ctx.author} was kamikaized for {mute} minutes")
        except Exception as e:
            error(f"{ctx.author} failed to kamikaized for {mute} minutes", e)
        try:
            await member.timeout(datetime.now(jerusalem_tz) + timedelta(minutes=mute))
            info(f"{ctx.author} muted {member} for {mute} minutes")
        except Exception as e:
            error(f"{ctx.author} failed to muted {member} for {mute} minutes", e)
            
        await ctx.reply(f"{ctx.author.mention} убился об {member.mention}, оба получили мут на {mute} минут")
            
        
async def setup(bot):
    await bot.add_cog(kamikazeCog(bot))
    
    
