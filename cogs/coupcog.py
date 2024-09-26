from functools import wraps
from abc import ABC, abstractmethod

import sys, os; sys.path.insert(0, os.path.join(os.getcwd(), ''))
from __init__  import *


# Декоратор для проверки, существует ли игра в канале и началась ли она
def game_exists_and_started(check_started=False):
    def decorator(func):
        @wraps(func)
        async def wrapper(cog, ctx: Ctx, *args, **kwargs):
            game = cog.games.get(ctx.channel.id)
            if not game:
                await ctx.send(f"**Игра еще не создана. Используй команду `{PREFIX}create_coup` для создания игры.**")
                return
            if check_started and not game.started:
                await ctx.send(f"**Игра еще не началась. Используй команду `{PREFIX}start_coup` для начала игры.**")
                return
            return await func(cog, ctx, *args, **kwargs)
        return wrapper
    return decorator

# Декоратор для проверки, находится ли игрок в игре
def player_in_game():
    def decorator(func):
        @wraps(func)
        async def wrapper(cog, ctx: Ctx, *args, **kwargs):
            game = cog.games.get(ctx.channel.id)
            if not game:
                await ctx.send("**Игра еще не создана.**")
                return
            if ctx.author not in game.players:
                await ctx.send("**Ты не в игре чувак**")
                return
            return await func(cog, ctx, *args, **kwargs)
        return wrapper
    return decorator


class CoupCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.games = {}  # Хранение активных игр

    @commands.Cog.listener()
    async def on_ready(self):
        info("Coup cog is ready")

    @commands.command(name="create_coup")
    async def create_coup(self, ctx: commands.Context):
        if ctx.channel.id in self.games:
            await ctx.send("Игра уже идет в этом канале!")
        else:
            self.games[ctx.channel.id] = CoupGame(ctx.author)
            await ctx.send(f"Игра создана! Присоединяйся помощью команды `{PREFIX}join_coup`.")

    @commands.command(name="join_coup")
    @game_exists_and_started(check_started=False)
    async def join_coup(self, ctx: commands.Context):
        game: CoupGame = self.games.get(ctx.channel.id)

        game.add_player(ctx.author)
        await ctx.send(f"**{ctx.author.display_name} залетает в партию!**")

    @commands.command(name="start_coup")
    @game_exists_and_started(check_started=False)
    async def start_game(self, ctx: commands.Context):
        game: CoupGame = self.games.get(ctx.channel.id)
        if game.started:
            await ctx.send("**Игра уже идёт бро.**")
        else:
            if len(game.players) < 2:
                await ctx.reply("**Для начала игры нужно минимум 2 челикса.**")
            else:
                game.start()
                await ctx.send("**Поехали!**")
                await self.show_status(ctx)

    @commands.command(name="coup_action")
    @game_exists_and_started(check_started=True)
    @player_in_game()
    async def coup_action(self, ctx: commands.Context, action: str, target: commands.MemberConverter = None):
        game: CoupGame = self.games.get(ctx.channel.id)
        result = game.perform_action(ctx.author, action, target)
        await ctx.send(result)
        await self.show_status(ctx)

    async def show_status(self, ctx: commands.Context):
        game: CoupGame = self.games.get(ctx.channel.id)
        status = game.get_status()
        await ctx.send(status)

    @commands.command(name="end_coup")
    async def end_game(self, ctx: commands.Context):
        if ctx.channel.id in self.games:
            del self.games[ctx.channel.id]
            await ctx.send("Игра завершена.")
        else:
            await ctx.send("В этом канале нет активной игры.")

class Player:
    def __init__(self, user):
        self.user: discord.Member = user
        self.coins = 2
        self.cards = []

    @property
    def display_name(self):
        return self.user.display_name

    def __str__(self):
        return self.display_name
    
class CoupCards:
    class CoupCard(ABC):
        def __init__(self, name, description):
            self.name = name
            self.description = description

        def __str__(self):
            return self.name
        
        def take_tax(self): 
            """Взять из казны 3 монеты"""
            return 3
        
        def assassinate(self, target: Player, card_position):
            """Совершить убийство за 3 монеты"""
            return target.cards.pop(card_position-1)
        
        def steal(self, target: Player):
            """Изъять 2 монеты у другого игрока"""
            target.coins -= 2
        
        def exchange(self):
            """Обмен картами с Двором"""
            return 'exchange'
        
        def interrogation(self):
            """Обменять карту с Двором или обменять карту противника с Двором"""
            return "Допрос: Обменена карта с Двором или обменена карта противника с Двором"
        
        def block_steal(self):
            """Наложить вето на воровство"""
            return "Блокировано"
        
        def block_tax(self):
            """Наложить вето на взятие налогов"""
            return "Блокировано"
        
        def block_assassinate(self):
            """Наложить вето на убийство"""
            return "Блокировано"
        

        
    class Governor(CoupCard):
        def __init__(self):
            super().__init__(
                name="Губернатор", 
                description="Взять из казны **3** монеты и наложить **вето** на **Помощь извне**."
            )

        def take_tax(self):
            """Взять из казны 3 монеты"""
            return super().take_tax()

        def block_tax(self):
            """Наложить вето на Помощь извне"""
            return super().block_tax()

    class Assassin(CoupCard):
        def __init__(self):
            super().__init__(
                name="Убийца", 
                description="Отдать в казну **3** монеты и **совершить убийство**. Княжна может наложить **вето**."
            )

        def assassinate(self):
            """Совершить убийство за 3 монеты"""
            return super().assassinate()


    class Princess(CoupCard):
        def __init__(self):
            super().__init__(
                name="Княжна", 
                description="Наложить **вето** на **Убийство**."
            )

        def block_assassinate(self):
            """Наложить вето на Убийство"""
            return super().block_assassinate()

    class Policeman(CoupCard):
        def __init__(self):
            super().__init__(
                name="Полицейский", 
                description="**Изъять 2 монеты** у другого игрока. **Советник**, **Следователь** или **Полицейский** могут наложить **вето**."
            )

        def steal(self, target):
            """Изъять 2 монеты у другого игрока"""
            return super().steal(target)

        def block_steal(self):
            """Наложить вето на Воровство"""
            return super().block_steal()

    class Counselor(CoupCard):
        def __init__(self):
            super().__init__(
                name="Советник", 
                description="**Обмен картами с Двором**. **Советник**, **Следователь** или **Полицейский** могут наложить **вето** на **Воровство**."
            )

        def exchange(self):
            """Обмен картами с Двором"""
            return super().exchange()

        def block_steal(self):
            """Наложить вето на Воровство"""
            return super().block()

    class Investigator(CoupCard):
        def __init__(self):
            super().__init__(
                name="Следователь", 
                description="**Обмен одной картой с Двором** или **обмен карты противника с Двором**. **Следователь**, **Советник** или **Полицейский** могут наложить **вето** на **Воровство**."
            )

        def interrogation(self):
            """Обменять карту с Двором или обменять карту противника с Двором"""
            return super().interrogation()

        def block_steal(self):
            """Наложить вето на Воровство"""
            return super().block_steal()



class CoupGame:
    def __init__(self, host):
        self.host = host
        self.players = []
        self.started = False

    def add_player(self, player):
        self.players.append(player)

    def start(self):
        self.started = True

    def get_status(self):
        return f"**Игра начата!**\n**Игроки:** {', '.join([player.display_name for player in self.players])}"

    def perform_action(self, player, action, target):
        # Логика выполнения действий игроками
        pass

async def setup(bot):
    await bot.add_cog(CoupCog(bot))
