import requests
from datetime import datetime, timedelta

from __init__ import *


class TeammateCog(commands.Cog, name="Find teammates commands"):

    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        """! on_ready - Событие, которое вызывается при готовности кога
        @return Сообщение о готовности кога"""
        info(f"TeammateCog cog is ready")

    @commands.command(brief="Поиск тиммейта")
    async def find_teammate(self, ctx, *args):
        
        """! find_teammate - Команда для поиска тиммейта"""
        
        search = await ctx.send("Поиск...")

        if len(args) == 3 and args[2].isdigit() and args[1].startswith("https://store.steampowered.com/app/"):
            await self.handle_valid_input(ctx, args, search)
        elif len(args) == 3 and not args[2].isdigit():
            await search.edit(content=f"{args[2]} не является числом")
        elif len(args) != 3:
            await search.edit(
                content=f"Команда должна быть введена с 3 аргументами\n?findteammate `ссылка на steam` `ссылка на игру в steam` `время в часах`")
        else:
            await search.edit(content="Ссылка на игру не действительна")

    async def handle_valid_input(self, ctx, args, search):
        """! handle_valid_input - Обработка валидного ввода"""
        try:
            response = requests.get(args[0])
            response.raise_for_status()

            if "Указанный профиль не найден." not in response.text:
                await self.process_valid_profile(ctx, args, search)
            else:
                await search.edit("Указанный профиль не найден.")

        except requests.RequestException as e:
            await search.edit(f"Ошибка при запросе, попробуйте еще раз")

    async def process_valid_profile(self, ctx, args, search):
        """! process_valid_profile - Обработка валидного профиля"""
        if db.user_exists(ctx.message.author.id, args[1]):
            await self.handle_existing_user(ctx, args, search)
        else:
            await self.handle_new_user(ctx, args, search)

    async def handle_existing_user(self, ctx, args, search):
        """! handle_existing_user - Обработка существующего пользователя"""
        exit_time = str(db.get_exit_time(ctx.message.author.id))
        await search.edit(content=f"Вы уже стоите в очереди на эту игру до {exit_time[2:-3]}")
        await self.send_ready_gamers(ctx, args, search)

    async def handle_new_user(self, ctx, args, search):
        """! handle_new_user - Обработка нового пользователя"""
        time = int(args[2])
        exit_time = str((datetime.now() + timedelta(hours=time)).strftime("%H:%M"))
        db.add_gamer(ctx.message.author.id, args[0], args[1], exit_time,
                     str((datetime.now() + timedelta(hours=time))))
        TeammateCog.send_ready_gamers(self, ctx, args, search)

    async def send_ready_gamers(self, ctx, args, search):
        """! send_ready_gamers - Отправка готовых игроков"""
        gamers = db.get_gamers(args[1])

        if gamers is not None:
            new_gamers = self.filter_and_update_gamers(gamers)

        if len(new_gamers) > 0:
            gamers = "".join(new_gamers)
            em = discord.Embed(title="Свободные игроки для вашей игры", description=gamers,
                               color=discord.Colour.random())
            await ctx.send(embed=em)
        else:
            await search.edit(content="В данный момент нет игроков на эту игру")

    def filter_and_update_gamers(self, gamers):
        """! filter_and_update_gamers - Фильтрация и обновление игроков"""
        new_gamers = []

        for user in gamers:
            user = db.remove_special_characters(str(user))
            exit_time2 = str(db.get_whole_time(user))
            datetime_object = datetime.strptime(exit_time2[2:-6], "%Y-%m-%d %H:%M:%S.%f")

            if datetime.now() > datetime_object:
                db.delete_user(user)
            else:
                exit_time1 = str(db.get_exit_time(user))
                stroke = f"<@{user}> свободен до `{exit_time1[2:-3]}`\n"
                new_gamers.append(stroke)

        return new_gamers


async def setup(bot):
    await bot.add_cog(TeammateCog(bot))
