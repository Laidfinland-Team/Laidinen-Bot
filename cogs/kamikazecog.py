
from __init__ import *
import random


kam_list = []

class kamikazeCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener() # This is a listener, like @bot.event
    async def on_ready(self):
        info("Kamikaze cog is ready")
        
    def cog_check(self, ctx: Ctx):
        async def f():
            await atrys(ctx.reply, "Этого пользователя нельзя обижать :shield: ")
            return False
        
        if ctx.message.reference:
            author_id = ctx.message.reference.resolved.author.id
        else:
            author_id = None
        if ctx.message.mentions:
            mention_id = ctx.message.mentions[0].id
        else:
            mention_id = None
            
        if mention_id not in PROTECTED_MEMBERS_IDS and author_id not in PROTECTED_MEMBERS_IDS:
            return True
        else:
            return f()
        
    
    @commands.command() # This is a command, like @bot.command()
    #@is_disabled()
    async def kamikaze(self, ctx: Ctx, member: discord.Member = None):
        
        if ctx.message.reference and not member:
            member = ctx.message.reference.resolved.author
        elif not member:
            await ctx.reply("Укажи жертву😈")
            return
            
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
            
        await ctx.reply(f"{ctx.author.mention} убился об {member.mention}💥\n-# оба получили мут на {mute} минут")
            
        
async def setup(bot):
    await bot.add_cog(kamikazeCog(bot))
    
    
