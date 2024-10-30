import discord.types
from __init__ import *
from datetime import datetime
import PIL
import random


LAST_CAT = True

CAT_DIR = r"cogs\catcog"
PLEASE_CAT_CHANNEL = 1156941990672466020 # Основной 
PLEASE_CAT_DURECTION = 3 * 3600 # 3 hours

LAST_CAT_DIR = r"light_databases\last_cat.json"

COMMAND_REACTION = ":pinkheart:1176964995695771719"
CAT_REACTION = "🔥"

EMOJI_LIST = """:C_beluga::C_comfortik::C_donate::C_dust::C_eww::C_hehe::C_hmm::C_mind::C_nothehe::C_ohh::C_shy::C_smirk::C_uwu::C_uwux2::C_wink::I_GigaChad::A_aww::A_blush::A_dem::A_scared::M_acup::M_affection::M_alright::M_cheers_mate::M_cluelesshappy::M_disturbed::M_eepy_not_interested::M_for_real::M_glasseshappy::M_guts_uncanny::M_hehshiiit::M_nyeeeeh::M_oof::M_pohuy::M_really_nibba::M_senkowow::M_smug_male::M_smugface::M_tired_af::L_goal::L_imba::L_plusrep::L_baza::L_eee::P_wow::a_hem::blush_love::cholera_photoresizer::emoji_125::despair::cute::coolguy::footfetish::masunya_a::masunya_angel::masunya_dies::masyunyapencil27::masunya_sexy::masunya_rofls::masunya_nyeeeeh::masunya_no::masunya_idgaf::masunya_forreal::masunya_drochesh::masunya_disturbed::spaniard::wait_what::milya_baza::milya_baka::yo::zen_horror:
             """.split(":")
             
for name in EMOJI_LIST:
    if name == "" or " " in name:
        EMOJI_LIST.remove(name)

class CatCog(commands.Cog):
    def __init__(self, bot):
        self.bot: commands.Bot = bot
        self.last_data = None
        self.cat_files = []
        self.server_emojis = []
        
        for filename in os.listdir(CAT_DIR):
            if True in [filename.endswith(f) for f in ['.png', 'jpg', 'jpeg', 'gif', 'webp']]:
                self.cat_files.append(filename)
            
                
    @commands.Cog.listener() # This is a listener, like @bot.event
    async def on_ready(self):
        self.load_archive()
        if LAST_CAT:
            self.hourly_check.start()
        info("Cat cog is ready")
        
        
    @tasks.loop(hours=1) 
    async def hourly_check(self):
        now = datetime.now()
        if self.last_data:
            last_data = datetime.strptime(self.last_data, "%Y-%m-%d %H:%M:%S")
            if (now - last_data).total_seconds() >= PLEASE_CAT_DURECTION:
                await self.please_send_cat(False)
    
    @commands.command()
    @is_hellcat()
    async def psc(self, ctx: Ctx):
        await self.please_send_cat(ctx)
    
    @commands.command()
    @is_hellcat()
    async def please_send_cat(self, ctx: Ctx = None):
        channel = bot.get_channel(PLEASE_CAT_CHANNEL)
        await channel.send("Пожалуйста, пришлите котика `?cat` - это важно!🐾")
        if ctx:
            if ctx.message:
                await ctx.message.add_reaction("✅")
        info("Please send cat message sent")
        
        
    
    @commands.command()
    async def cat(self, ctx: Ctx):
        
        for e in ctx.guild.emojis:
            self.server_emojis.append(e)
        file = random.choice(self.cat_files)
        reaction = await ctx.guild.fetch_emoji(int(COMMAND_REACTION.split(":")[2]))
        data = {
                'count':1,
                'me':True,
                'emoji':reaction,
                'me_burst':False,
                'count_details':{'normal':1, 'burst':0},
                'burst_colors':[]
            }
        
        
        reaction = discord.Reaction(message=ctx.message, data=data, emoji=reaction)
        try:
            await ctx.message.add_reaction(reaction)
        except:
            error("Message not found")
            
        async with ctx.typing():
            server_emoji_names = []
            for e in await ctx.guild.fetch_emojis():
                if type(e) == discord.emoji.Emoji:
                    server_emoji_names.append({e.name:e.id})
                
            random_emoji = random.choice(EMOJI_LIST)    
                
                
            emoji = f"<:{random_emoji}:{str(server_emoji_names[[list(d.keys())[0] for d in server_emoji_names].index(random_emoji)]).split(':')[1].replace('}','').replace(' ', '')}>"
            
            message = await ctx.send(content=emoji, file=discord.File(f"{CAT_DIR}/{file}"))
            
            reaction = discord.Reaction(message=ctx.message, data=data, emoji=CAT_REACTION)
            
            await message.add_reaction(reaction)
            self.last_data = datetime.now(jerusalem_tz).strftime("%Y-%m-%d %H:%M:%S") 
            self.save_archive()
            if 'laid' in file:
                output(ctx.channel, f"Laid cat image sent to {ctx.author.name}" + Fore.RED + " (laid)") 
            else:
                output(ctx.channel, f"Cat image sent to {ctx.author.name}")
                
    def load_archive(self):
        try:
            with open(LAST_CAT_DIR, "r", encoding="utf-8") as f:
                last_data = json.load(f)
                if last_data:
                    self.last_data = last_data
        except Exception as e:
            self.last_data = None
            error("Failed to load last cat data", e)
                 


    def save_archive(self):
        try:
            with open(LAST_CAT_DIR, "w", encoding="utf-8") as f:
                
                json.dump(self.last_data, f, ensure_ascii=False, indent=4)
                
        except:
            error("Failed to save last cat data")
            
            
        
async def setup(bot):
    await bot.add_cog(CatCog(bot))