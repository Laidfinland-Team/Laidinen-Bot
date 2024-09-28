import random
from datetime import timedelta
import datetime

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
    
    
    
    def __init__(self, ctx):
        super().__init__(timeout=TIMEOUT)
        self.ctx = ctx
        self.players: list[discord.Member] = []
        self.winner = None
        
        self.embed = discord.Embed(
        title="Камень, ножницы, бумага",
        description="Выберите один из вариантов",
        color=discord.Color.yellow()
    )
    
    async def interaction_check(self, interaction: discord.Interaction):
        return True#interaction.user.id == self.ctx.message.author.id
    
    async def end_of_game(self, interaction: discord.Interaction):
        if len(self.players) >= 2:
            player1, player2 = self.players
            if player1[1] == player2[1]:
                self.winner =f"Ничья, {player1[0]} против {player2[0]}\n-# Никто не победил, оба выбрали {player1[1]}(("
                
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
        

TIMEOUT = 10  # Общее время ожидания завершения игры
failed_texts = ["отбрасывает конки", "сдох", "дединсайд", "дедаутсайд", "дед", "поймал между глаз", "покрасил асфальт", "лох", "слит", "слит как ботик", "щавель"]
class DuelGame(discord.ui.View):
    class Confirm(discord.ui.View):
        def __init__(self, ctx: Ctx):
            super().__init__(timeout=TIMEOUT)
            self.ctx = ctx
            self.value = None
            self.message: discord.Message = None
            
        async def interaction_check(self, interaction: discord.Interaction) -> bool:
            # Ограничение взаимодействия только для зарегистрированных игроков
            return interaction.user == self.ctx.message.mentions[0]
        
        async def on_timeout(self):
            # Действия, если время ожидания истекло
            await self.message.edit(view=None)
            self.value = False
            
        @discord.ui.button(label="Принять вызов", style=discord.ButtonStyle.green)
        async def confirm(self, interaction: discord.Interaction, button: discord.ui.Button):
            self.value = True
            await self.message.edit(view=None)
            self.stop()
            
        @discord.ui.button(label="Струсить", style=discord.ButtonStyle.red)
        async def cancel(self, interaction: discord.Interaction, button: discord.ui.Button):
            self.value = False
            await self.message.edit(view=None)
            self.stop()
    
    class StartGame(discord.ui.View):
        def __init__(self, ctx: Ctx, players: list[discord.Member]):
            super().__init__(timeout=TIMEOUT)
            self.ctx = ctx
            self.value = False
            self.players = players
            self.confirmed = []
            
        async def interaction_check(self, interaction: discord.Interaction) -> bool:
            # Ограничение взаимодействия только для зарегистрированных игроков
            return interaction.user in self.players and not interaction.user in self.confirmed
        
        async def on_timeout(self):
            # Действия, если время ожидания истекло
            await atrys(self.ctx.message.delete)
            self.value = False
            
        @discord.ui.button(label="Начать", style=discord.ButtonStyle.green)
        async def start(self, interaction: discord.Interaction, button: discord.ui.Button):
            self.value = True
            self.confirmed.append(interaction.user)
            self.clear_items()
            await interaction.response.defer()
            self.stop()
            
        
    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        # Ограничение взаимодействия только для зарегистрированных игроков
        return interaction.user in self.players
    
    async def on_timeout(self):
        # Действия, если время ожидания истекло
        if not self.winner:
            await self.ctx.message.edit(embed=self.timeout_embed.format(self.players[0], self.players[1]), view=None)
        
    @discord.ui.button(label="Огонь", style=discord.ButtonStyle.red)
    async def shoot_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        # Вычисление времени реакции игрока
        reaction_time = (discord.utils.utcnow() - self.start_time).total_seconds()

        # Проверка, что игрок ещё не нажал кнопку
        if interaction.user not in self.results:
            self.results[interaction.user] = reaction_time
            start_embed = self.start_embed
            start_embed.description = f"{interaction.user.display_name} выстрелил!💥"
            await interaction.message.edit(embed=start_embed)
        
        if len(self.results) == 2 and not self.winner:
            await interaction.response.edit_message(view=None)
            await self.determine_winner()
        else:
            await interaction.response.defer()
            
                
    def __init__(self, ctx: Ctx):
        super().__init__(timeout=TIMEOUT)
        self.ctx = ctx
        self.players: list[discord.Member] = []
        self.start_confirms = []
        self.winner = None
        self.time = None
        self.start_time = None  # Время, когда кнопка появляется
        self.results = {}  # Для хранения времени нажатия
        self.mute = random.randint(1, 15)

        embed = discord.Embed(
        title="Дуэль",
        description="Побеждает тот, кто точнее прицелится к назначенному времени!",
        color=discord.Color.dark_gold()
    )
        self.description_embed = FormatEmbed(
            title="Дуэль между {} и {}",
            description="### Что бы попасть, целься как можно ближе к {} секундам после появления кнопки!",
            color=discord.Color.light_gray()
        )
        self.start_embed = FormatEmbed(
            title="Дуэль между {} и {}",
            description="### Жди {} секунд и стреляй! ⏱",
            color=discord.Color.lighter_gray()
        )   
        self.end_embed = FormatEmbed(
            title="Дуэль между {} и {}",
            description="### Победитель: {}!\n**Цель: {}** \n\nрезультат: {} \nразница {}\n\n### Плохой ковбой: {}\nрезультат: {} \nразница {}",
            color=discord.Color.yellow()
        )
        self.timeout_embed = FormatEmbed(
            title="Дуэль между {} и {}",
            description="# Время вышло сосунки!",
            color=discord.Color.darker_gray()
        )   
    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        # Ограничение взаимодействия только для зарегистрированных игроков
        return interaction.user in self.players
    
    async def on_timeout(self):
        # Действия, если время ожидания истекло
        if not self.winner:
            await self.ctx.message.edit(embed=self.timeout_embed.format(self.players[0], self.players[1]), view=None)


    async def start_game(self, message: discord.Message = None, ready_m: discord.Message = None):
        # Оповещаем игроков
        if not message:
            self.time = random.randint(1, 6)
            view = self.StartGame(self.ctx, self.players)
            message = await self.ctx.channel.send(embed=self.description_embed.format(self.players[0].name, self.players[1].name, self.time), view=view)
            self.ctx = await bot.get_context(message)
            # Задержка перед началом таймера
        else:
            view = self.StartGame(self.ctx, self.players)
            view.confirmed = [True]
            message = await message.edit(embed=self.description_embed.format(self.players[0].name, self.players[1].name, self.time), view=view)
            self.ctx = await bot.get_context(message)
        await view.wait()
        ready_m2 = discord.Message
        if ready_m:
            ready_m2 = ready_m
            
        ready_m = await atrys(self.ctx.send, f"**{view.confirmed[0].name if type(view.confirmed[0]) == discord.member.Member else view.confirmed[1].name}** готов😎")
        
        if view.value is False:
            return await self.ctx.message.edit(embed=self.timeout_embed.format(self.players[0], self.players[1]), view=None)
        elif view.value is True and len(view.confirmed) < 2:
            return await self.start_game(message, ready_m)
        
        old_embed = self.start_embed
        self.start_embed.description = "Жди {} секунд и стреляй! ⏱"
        
        await self.ctx.message.edit(embed=self.start_embed.format(self.players[0].name, self.players[1].name, self.time), view=None)
        await atrys(ready_m.delete)
        await atrys(ready_m2.delete)
        await asyncio.sleep(random.uniform(2, 3))  # Немного рандома перед показом кнопки
        self.start_embed = old_embed
        await self.ctx.message.edit(embed=self.start_embed.format(self.players[0].name, self.players[1].name, self.time), view=self)

        # Устанавливаем время появления кнопки
        self.start_time = discord.utils.utcnow()

        # Запуск обратного отсчёта
        await asyncio.sleep(7)  # Игрокам даётся 7 секунд для реакции

        if not self.winner:
            self.on_timeout()

    @private
    async def determine_winner(self):
        if not self.results:
            await self.ctx.message.edit(embed=self.timeout_embed.format(self.players[0], self.players[1]), view=None)
            return

        # Определение победителя на основе реакции ближе к 7 секундам
        closest_player: discord.Member = min(self.results, key=lambda player: abs(self.results[player] - self.time))
        self.winner = closest_player
        self.loser = [p for p in self.players if p != self.winner][0]

        await self.ctx.message.edit(embed=self.end_embed.format(self.players[0].name, self.players[1].name, closest_player.mention, f"{self.time} (секунд)", f'{self.results[self.winner]:.3f}', round(abs(self.results[closest_player] - self.time), 3), self.loser.mention, f'{self.results[self.loser]:.3f}', round(abs(self.results[self.loser] - self.time), 3)), view=None)
        await self.ctx.send(f"**{self.loser}** {random.choice(failed_texts)}\n-# И отлетает в мут на **{self.mute}** минут")
        
        try:
            await self.loser.timeout(datetime.now(jerusalem_tz) + timedelta(minutes=self.mute))
            info(f"{self.loser} was muted to {self.mute} minutes")
        except Exception as e:
            error(f"Timeout error: {e}")
        
        

    


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
        
    
    @commands.command(brief="Дуэль")
    async def duel(self, ctx: Ctx, member: discord.Member = None):
        duel_invite = DuelGame.Confirm(ctx)
        
        if member is None:
            if ctx.message.reference.resolved.author:
                member = ctx.message.reference.resolved.author
            else:
                return await ctx.send("Укажите пользователя, которого вы хотите вызвать на дуэль")
            
        message = await ctx.channel.send(content=f"# 🧤\n{member.mention}\n\n**{ctx.message.author.mention} вызывает тебя на дуэль!**", view=duel_invite)
        duel_invite.message = message
        
        await duel_invite.wait()
        
        if duel_invite.value:
            duel = DuelGame(ctx)
            duel.players = [ctx.message.author, member]
            await duel.start_game()
        else:
            await ctx.reply(f"{member.mention} зассал🤡")
    
    
    
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