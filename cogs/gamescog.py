import random
from datetime import timedelta

from __init__ import *

TIMEOUT = 20 ## Время таймаута кнопок
MUTE = timedelta(minutes=15) # Время мута после смерти
DIED_CHANCE = 5 # Пиши только делитель => 1 / DIED_CHANCE ## Шанс умереть

class Russian_roulette(discord.ui.View):
    success_messages = ["Сегодня тебе везёт :)", "Ты выжил", "Ты победил", "**Удача исчерпана**", "Сходи в лотерею, сегодня твой день", "у тебя всё получится 🌹"] ## Сообщения при осечке
    failure_messages = ["БУМ и ты отлетаешь!", "**YOU DIED**", "Пока-пока!)", "Да ты снайпер! Точно в цель)", "Ну, в любви уже не повезёт"] ## Сообщения при выстреле
    
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
        self.ctx: Ctx = ctx
        
    async def interaction_check(self, interaction: discord.Interaction):
        return interaction.user.id == self.ctx.message.author.id

    @discord.ui.button(label='Спуск', style=discord.ButtonStyle.red)
    async def shoot(self, interaction: discord.Interaction, button: discord.ui.Button):
        '''! shoot - Функция для обработки нажатия кнопки "Спуск"'''
        
        if not await Russian_roulette.interaction_check(self, interaction):
            return
                
        if random.randint(0, DIED_CHANCE):
            await self.ctx.send(Russian_roulette.success_messages[random.randint(0, len(Russian_roulette.success_messages)) - 1])
            await interaction.message.edit(embed=Russian_roulette.success_embed)
            self.died = False
        else:
            await self.ctx.send(Russian_roulette.failure_messages[random.randint(0, len(Russian_roulette.failure_messages) ) - 1])
            await interaction.message.edit(embed=Russian_roulette.failure_embed)
            self.died = True
        self.value = True
        await interaction.message.edit(view=None)
        self.stop()
        
    @discord.ui.button(label='Зассал', style=discord.ButtonStyle.gray)
    async def cancel(self, interaction: discord.Interaction, button: discord.ui.Button):
        
        '''! cancel - Функция для обработки нажатия кнопки "Зассал"'''
        self.value = False
        await self.ctx.message.delete()
    
        await interaction.message.delete()
        self.stop()
        
class Rock_paper_scissors(discord.ui.View):
    
    embed = discord.Embed(
        title="Камень, ножницы, бумага",
        description="Выберите один из вариантов",
        color=discord.Color.yellow()
    )
    
    def __init__(self, ctx):
        super().__init__(timeout=TIMEOUT)
        self.ctx = ctx
        self.players: list[discord.Member] = []
        self.winner = None
    
    async def interaction_check(self, interaction: discord.Interaction):
        return True#interaction.user.id == self.ctx.message.author.id
    
    async def end_of_game(self, interaction: discord.Interaction):
        if len(self.players) >= 2:
            player1, player2 = self.players
            if player1[1] == player2[1]:
                self.winner ="Ничья"
                
            elif player1[1] == "rock" and player2[1] == "scissors":
                self.winner = f"**<@{player1[0].id}> победил <@{player2[0].id}>!**\n-# **Камень** отмудохал **ножницы**"
            elif player1[1] == "scissors" and player2[1] == "paper":
                self.winner = f"**<@{player1[0].id}> победил <@{player2[0].id}>!**\n-# **Ножницы** почикали **бумагу**"
            elif player1[1] == "paper" and player2[1] == "rock":
                self.winner = f"**<@{player1[0].id}> победил <@{player2[0].id}>!**\n-# **Бумага** схавала **камень**"
                
            elif player2[1] == "rock" and player1[1] == "scissors":
                self.winner = f"**<@{player2[0].id}> победил <@{player1[0].id}>!**\n-# **Камень** отмудохал **ножницы**"
            elif player2[1] == "scissors" and player1[1] == "paper":
                self.winner = f"**<@{player2[0].id}> победил <@{player1[0].id}>!**\n-# **Ножницы** почикали **бумагу**"
            elif player2[1] == "paper" and player1[1] == "rock":
                self.winner = f"**<@{player2[0].id}> победил <@{player1[0].id}>!**\n-# **Бумага** схавала **камень**"
            
            self.embed.description = f"**Игра окончена!**\n{self.winner}"
            await interaction.message.edit(embed=self.embed, view=None)
            self.stop()

    @discord.ui.button(label='🧱', style=discord.ButtonStyle.primary)
    async def rock(self, interaction: discord.Interaction, button: discord.ui.Button):
        
        '''! rock - Функция для обработки нажатия кнопки "Камень"'''
        if not interaction.user in [player[0] for player in self.players]:
            self.players.append((interaction.user, "rock"))
        await self.end_of_game(interaction)
        await interaction.response.defer()
        
    @discord.ui.button(label='✂', style=discord.ButtonStyle.primary)
    async def scissors(self, interaction: discord.Interaction, button: discord.ui.Button):
        
        '''! scissors - Функция для обработки нажатия кнопки "Ножницы"'''
        if not interaction.user in [player[0] for player in self.players]:
            self.players.append((interaction.user, "scissors"))
        await self.end_of_game(interaction)
        await interaction.response.defer()
        
    @discord.ui.button(label='📰', style=discord.ButtonStyle.primary)
    async def paper(self, interaction: discord.Interaction, button: discord.ui.Button):
        
        '''! paper - Функция для обработки нажатия кнопки "Бумага"'''
        if not interaction.user in [player[0] for player in self.players]:
            self.players.append((interaction.user, "paper"))
        await self.end_of_game(interaction)
        await interaction.response.defer()

class GamesCog(commands.Cog, name="Games"):
    
    """! GamesCog - Ког с командами для игры"""

    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        
        """! Событие, которое вызывается при готовности кога"""
        
        info("GamesCog cog is ready")
        
        
    @commands.command(brief="Камень, ножницы, бумага")
    async def rps(self, ctx: Ctx):
        await self.rock_paper_scissors(ctx)
            
    @commands.command(brief="Камень, ножницы, бумага")
    async def rock_paper_scissors(self, ctx: Ctx):
        view = Rock_paper_scissors(ctx)
        ctx: discord.Message = await ctx.send(embed=view.embed, view=view)
        
        await view.wait()
        embed = discord.Embed(title="Камень, ножницы, бумага", description="**Соперник убежал...**", color=discord.Color.dark_gray())
        if view.winner is None:
            await ctx.edit(embed=embed, view=None)
        
    
    
    @commands.command(brief="Русская рулетка")
    async def rr(self, ctx: Ctx, member: discord.Member = None):
        await self.russian_roulette(ctx, member)

    @commands.command(brief="Русская рулетка")
    async def russian_roulette(self, ctx: Ctx, member: discord.Member = None):
        
        """! Команда для игры в русскую рулетку"""
        
        if member:
            embed = discord.Embed(title=f"Тебе предложили сыграть в Русскую рулетку", description=f"Что бы сыграть введи команду `{PREFIX}russian_roulette`\nУ тебя лишь одна жизнь.\nЕсли погибнешь получишь мут на {MUTE} минут", color=discord.Color.red())
            embed.set_footer(text=f"Игра с {ctx.message.author.name}")
            
            await ctx.send(content=f"<@{member.id}>", embed=embed)
            await ctx.send( content=f"https://media1.tenor.com/m/lm8iTuh1lRIAAAAd/gun-weapon.gif")
        
        else:
            embed = discord.Embed(title="Русская Рулетка", description=f"У тебя лишь одна жизнь.\nЕсли погибнешь получишь мут на {MUTE} минут", color=discord.Color.red())
            
            view = Russian_roulette(ctx)
            
            await ctx.send(embed=embed, view=view)
            await view.wait()
            
            if view.value is None:
                info(ctx.channel.name + ': Russian Roulette: Timed out')
                await ctx.send('Время вышло сосунок...')
                
            elif view.value:
                info(ctx.channel.name + ': Russian Roulette:  Russian_rouletteed')
                    
            else:
                info(ctx.channel.name + ': Russian Roulette:  Cancelled')
                
            if view.died:
                try:
                    await ctx.author.timeout(MUTE)
                    info(ctx.channel.name + ': Russian Roulette:  Muted')
                except Exception as e:
                        error(f"Timeout error: {e}")

async def setup(bot):
    await bot.add_cog(GamesCog(bot))