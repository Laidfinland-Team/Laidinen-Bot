import random
from datetime import timedelta

from __init__ import *

TIMEOUT = 20 ## Время таймаута кнопок
MUTE = timedelta(minutes=15) # Время мута после смерти
DIED_CHANCE = 10 # Пиши только делитель => 1 / DIED_CHANCE ## Шанс умереть

class Confirm(discord.ui.View):
    success_messages = ["Сегодня тебе везёт :)", "Ты выжил", "Ты победил"] ## Сообщения при осечке
    failure_messages = ["БУМ и ты отлетаешь!", "**YOU DIED**", "Пока-пока!)", "Да ты снайпер! Точно в цель)", ] ## Сообщения при выстреле
    
    ## Эмбеды для сообщений при осечке
    success_embed = discord.Embed(
        title="ПУСТО",  
        color=discord.Color.lighter_grey()
        )
    
    ## Эмбеды для сообщений при выстреле
    failure_embed = discord.Embed(
        title="ВЫСТРЕЛ!!!",  
        color=discord.Color.red()
        )
    
    def __init__(self, ctx):
        super().__init__(timeout=TIMEOUT)
        self.value = None
        self.died = False
        self.ctx = ctx

    @discord.ui.button(label='Спуск', style=discord.ButtonStyle.red)
    async def shoot(self, interaction: discord.Interaction, button: discord.ui.Button):
        
        '''! shoot - Функция для обработки нажатия кнопки "Спуск"'''
        
        if random.randint(0, DIED_CHANCE):
            await self.ctx.send(Confirm.success_messages[random.randint(0, len(Confirm.success_messages)) - 1])
            await interaction.message.edit(embed=Confirm.success_embed)
            self.died = False
        else:
            await self.ctx.send(Confirm.failure_messages[random.randint(0, len(Confirm.failure_messages) ) - 1])
            await interaction.message.edit(embed=Confirm.failure_embed)
            self.died = True
        self.value = True
        self.stop()
     
    @discord.ui.button(label='Зассал', style=discord.ButtonStyle.gray)
    async def cancel(self, interaction: discord.Interaction, button: discord.ui.Button):
        
        '''! cancel - Функция для обработки нажатия кнопки "Зассал"'''
        self.value = False
        await self.ctx.message.delete()
    
        await interaction.message.delete()
        self.stop()

class GamesCog(commands.Cog, name="Games"):
    
    """! GamesCog - Ког с командами для игры"""

    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        
        """! Событие, которое вызывается при готовности кога"""
        
        info("GamesCog cog is ready")

    @commands.command(brief="Русская рулетка")
    async def russian_roulette(self, ctx):
        
        """! Команда для игры в русскую рулетку"""
        
        embed = discord.Embed(title="Русская Рулетка", description=f"У тебя лишь одна жизнь.\nЕсли погибнешь получишь мут на {MUTE} минут", color=discord.Color.red())
        
        view = Confirm(ctx)
        
        await ctx.send(embed=embed, view=view)
        await view.wait()
        
        if view.value is None:
            info(ctx.channel.name + ': Russian Roulette: Timed out')
            await ctx.send('Время вышло сосунок...')
            
        elif view.value:
            info(ctx.channel.name + ': Russian Roulette:  Confirmed')
                
        else:
            info(ctx.channel.name + ': Russian Roulette:  Cancelled')
            
        if view.died:
            try:
                await ctx.author.timeout(MUTE)
            except Exception as e:
                    error(f"Timeout error: {e}")

async def setup(bot):
    await bot.add_cog(GamesCog(bot))