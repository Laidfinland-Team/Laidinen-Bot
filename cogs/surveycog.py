import sys, os; #sys.path.insert(0, os.path.join(os.getcwd(), ''))

from __init__ import *

SURVEY_CHANNEL_ID = 1291735880754659328

CACHE_EXPIRATION_TIME = 3 # Мин время перед тем как пользователь сможет поставить ещё реакцию на опрос

"""Что бы отметить опрос как опрос с оценкой добавь в title emend-а надпись '(баллы)' или '(перевернутые баллы)'"""

class SurveyCog(commands.Cog):
    emoji_values = {
        1: '1️⃣',
        2: '2️⃣',
        3: '3️⃣',
        4: '4️⃣',
        5: '5️⃣',
        6: '6️⃣',
        7: '7️⃣',
        8: '8️⃣',
        9: '9️⃣'
    }
    """!!!Invert emoji_values!!!"""
    emoji_values = dict(zip(emoji_values.values(), emoji_values.keys()))
    
    def __init__(self, bot):
        self.bot = bot
        self.reaction_cache = []

    @commands.Cog.listener() # This is a listener, like @bot.event
    async def on_ready(self):
        info("Survey cog is ready")

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload: discord.RawReactionActionEvent):
        if payload.channel_id != SURVEY_CHANNEL_ID:
            return
        
        if payload.user_id not in self.reaction_cache:
            self.reaction_cache.append(payload.user_id)
            await self.wait_and_clear_cache(payload.user_id)
        else:
            return
        
        if self.reaction_cache:
            await asyncio.sleep(CACHE_EXPIRATION_TIME)
        
        
        channel = self.bot.get_channel(payload.channel_id)
        message: Message = await channel.fetch_message(payload.message_id)
        
        
        if not 'баллы' in message.embeds[0].title.lower():
            return
        if 'перевернутые баллы' in message.embeds[0].title.lower():
            reversed = True
        else:
            reversed = False
            
        grades = []    
        for r in message.reactions:
            if r.emoji in SurveyCog.emoji_values.keys():
                grades.append(SurveyCog.emoji_values[r.emoji])
                
        if payload.emoji.name in ['1️⃣', '2️⃣', '3️⃣', '4️⃣', '5️⃣', '6️⃣', '7️⃣', '8️⃣', '9️⃣']:
            avg = await self.calculate_survey(message, max(grades))
        else:
            return
            
        embed = message.embeds[0]
        embed.clear_fields()
        avg_grade = f"\n\n**{avg:.1f}**" if avg != '-' else f"\n\n**-**"
        embed.add_field(value=avg_grade, name=f"{"Средняя оценка" + " (перевернутая)" if reversed else "Средняя оценка"}")
        embed.add_field(value=f"{sum([r.count for r in message.reactions])-(max(grades))} чуваков", name="Проголосовало")
        embed.color = self.calculate_color(avg, max(grades), reversed)
        
        await message.edit(embed=embed)
        info(f"Survey {message.id} updated")
        
    @commands.Cog.listener()
    async def on_raw_reaction_remove(self, payload: discord.RawReactionActionEvent):
        await self.on_raw_reaction_add(payload)
        
    async def calculate_survey(self, message: discord.Message, max_grade):
        keys = ['1️⃣', '2️⃣', '3️⃣', '4️⃣', '5️⃣', '6️⃣', '7️⃣', '8️⃣', '9️⃣']
        reacts = {k: 0 for k in keys}
        for e in message.reactions:
            if e.emoji in ['1️⃣', '2️⃣', '3️⃣', '4️⃣', '5️⃣', '6️⃣', '7️⃣', '8️⃣', '9️⃣']:
                reacts[e.emoji] = e.count
        
        grade = -(max_grade*(max_grade+1))/2
        for k, v in reacts.items():
            grade += SurveyCog.emoji_values[k] * v
            
        avg = grade / (sum(reacts.values())-max_grade) if sum(reacts.values())-max_grade != 0 else '-'
        
        return avg
    
    async def wait_and_clear_cache(self, user_id):
        await asyncio.sleep(CACHE_EXPIRATION_TIME)
        self.reaction_cache.remove(user_id)
            
    def calculate_color(self, avg, max_grade, reversed=False):
        if avg == '-':
            return MAIN_COLOR
        elif avg <= max_grade / 3:
            return discord.Color.red() if not reversed else discord.Color.green()
        elif avg <= 2 * max_grade / 3:
            return discord.Color.yellow()
        else:
            return discord.Color.green() if not reversed else discord.Color.red()
                    
        
async def setup(bot):
    await bot.add_cog(SurveyCog(bot))