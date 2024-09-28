
from __init__ import *
import random

ALLOWED_CHANNELS = [1253000758534602902]


EMOJI_LIST = """:C_beluga::C_comfortik::C_donate::C_dust::C_eww::C_hehe::C_hmm::C_mind::C_nothehe::C_ohh::C_shy::C_smirk::C_uwu::C_uwux2::C_wink::I_GigaChad::A_aww::A_blush::A_dem::A_scared::M_acup::M_affection::M_alright::M_cheers_mate::M_cluelesshappy::M_disturbed::M_eepy_not_interested::M_for_real::M_glasseshappy::M_guts_uncanny::M_hehshiiit::M_nyeeeeh::M_oof::M_pohuy::M_really_nibba::M_senkowow::M_smug_male::M_smugface::M_tired_af::L_goal::L_imba::L_plusrep::L_baza::L_eee::P_wow::a_hem::blush_love::cholera_photoresizer::emoji_125::despair::cute::coolguy::footfetish::masunya_a::masunya_angel::masunya_dies::masyunyapencil27::masunya_sexy::masunya_rofls::masunya_nyeeeeh::masunya_no::masunya_idgaf::masunya_forreal::masunya_drochesh::masunya_disturbed::spaniard::wait_what::milya_baza::milya_baka::yo::zen_horror:
             """.split(":")
sex = ['жопу', 'рот', 'глаз', 'ухо', 'нос', 'пасть', 'пизду', 'член', 'попу', 'грудь', 'пупок', 'плечо', 'палец', 'голову', 'пятку', 'колено']
    
    
for name in EMOJI_LIST:
    if name == "" or " " in name:
        EMOJI_LIST.remove(name)
        
def toxic():
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            ctx: Ctx = args[1]
            if ctx.channel.id in ALLOWED_CHANNELS or ctx.message.author.guild_permissions.administrator:
                return await func(*args, **kwargs)
            else:
                return await ctx.reply("Эта команда не доступна в этом канале, пиздуй в <#1253000758534602902> 😈")
        return wrapper
    return decorator
        
class SexCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener() # This is a listener, like @bot.event
    async def on_ready(self):
        info("Sex cog is ready")
    
    async def create_emoji(self, ctx: Ctx):
        async with ctx.typing():
            server_emoji_names = []
            for e in await ctx.guild.fetch_emojis():
                if type(e) == discord.emoji.Emoji:
                    server_emoji_names.append({e.name:e.id})
                
            random_emoji = random.choice(EMOJI_LIST)    
                
                
            emoji = f"<:{random_emoji}:{str(server_emoji_names[[list(d.keys())[0] for d in server_emoji_names].index(random_emoji)]).split(':')[1].replace('}','').replace(' ', '')}>"
            return emoji
        
    @commands.command() # This is a command, like @bot.command()
    @toxic()
    async def sex(self, ctx: Ctx, member: discord.Member = None):
        
        if member in ['-help', 'help', '-h', 'h'] and not ctx.message.reactions:
            return await ctx.send(f"\n Вот всё что ты можешь сделать:\n**{[c.name for c in self.get_commands()]}**")
        elif ctx.message.reference:
            member = ctx.message.reference.resolved.author
        elif member is None:
            return await ctx.send(f"\n Вот всё что ты можешь сделать:\n**{[c.name for c in self.get_commands()]}**")
            
        emoji = await self.create_emoji(ctx)
        await ctx.send(f"{ctx.author.mention} жёстко выебал в {random.choice(sex)} {member.mention} {emoji}")
    
    @commands.command() # This is a command, like @bot.command()
    @toxic()
    async def kiss(self, ctx: Ctx, member: discord.Member = None):
        if ctx.message.reference:
            member = ctx.message.reference.resolved.author
            
        if member:
            emoji = await self.create_emoji(ctx)
            await ctx.send(f"{ctx.author.mention} засосал  {member.mention} прям в {random.choice(sex)} {emoji}")
        else: 
            await ctx.send("Укажите пользователя, которого вы хотите того)")
        
    @commands.command() # This is a command, like @bot.command()
    @toxic()
    async def hug(self, ctx: Ctx, member: discord.Member = None):
        if ctx.message.reference:
            member = ctx.message.reference.resolved.author
            
        if member:
            emoji = await self.create_emoji(ctx)
            await ctx.send(f"{ctx.author.mention} обнял {member.mention} за его {random.choice(sex)} {emoji}")
        else: 
            await ctx.send("Укажите пользователя, которого вы хотите того)")
        
    @commands.command() # This is a command, like @bot.command()
    @toxic()
    async def slap(self, ctx: Ctx, member: discord.Member = None):
        if ctx.message.reference:
            member = ctx.message.reference.resolved.author
        
        if member:
            emoji = await self.create_emoji(ctx)
            await ctx.send(f"{ctx.author.mention} шлепнул {member.mention} по {random.choice(sex)} {emoji}")
        else: 
            await ctx.send("Укажите пользователя, которого вы хотите того)")
    
    @commands.command() # This is a command, like @bot.command()
    @toxic()
    async def pat(self, ctx: Ctx, member: discord.Member = None):
        if ctx.message.reference:
            member = ctx.message.reference.resolved.author
            
        if member:
            emoji = await self.create_emoji(ctx)
            await ctx.send(f"{ctx.author.mention} погладил {member.mention} по {random.choice(sex)} {emoji}")
        else: 
            await ctx.send("Укажите пользователя, которого вы хотите того)")
        
    @commands.command() # This is a command, like @bot.command()
    @toxic()
    async def lick(self, ctx: Ctx, member: discord.Member = None):
        if ctx.message.reference:
            member = ctx.message.reference.resolved.author
            
        if member:
            emoji = await self.create_emoji(ctx)
            await ctx.send(f"{ctx.author.mention} облизал {member.mention} по {random.choice(sex)} {emoji}")
        else: 
            await ctx.send("Укажите пользователя, которого вы хотите того)")
        
    @commands.command() # This is a command, like @bot.command()
    @toxic()
    async def bite(self, ctx: Ctx, member: discord.Member = None):
        if ctx.message.reference:
            member = ctx.message.reference.resolved.author
            
        if member:
            emoji = await self.create_emoji(ctx)
            await ctx.send(f"{ctx.author.mention} укусил {member.mention} за {random.choice(sex)} {emoji}")
        else: 
            await ctx.send("Укажите пользователя, которого вы хотите того)")
        
    @commands.command() # This is a command, like @bot.command()
    @toxic()
    async def poke(self, ctx: Ctx, member: discord.Member = None):
        if ctx.message.reference:
            member = ctx.message.reference.resolved.author
            
        if member:
            emoji = await self.create_emoji(ctx)
            await ctx.send(f"{ctx.author.mention} ткнул {member.mention} в {random.choice(sex)} {emoji}")
        else: 
            await ctx.send("Укажите пользователя, которого вы хотите того)")
        
    @commands.command() # This is a command, like @bot.command()
    @toxic()
    async def sex_with(self, ctx: Ctx, member: discord.Member = None):
        if ctx.message.reference:
            member = ctx.message.reference.resolved.author
            
        if member:
            emoji = await self.create_emoji(ctx)
            await ctx.send(f"{ctx.author.mention} жёстко дал {member.mention} в {random.choice(sex)} {emoji}")
        else: 
            await ctx.send("Укажите пользователя, которого вы хотите того)")
        
        
        
async def setup(bot):
    await bot.add_cog(SexCog(bot))
    
    
