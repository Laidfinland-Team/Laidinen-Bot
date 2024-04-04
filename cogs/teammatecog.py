import requests
from datetime import datetime, timedelta
import json
import re
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

        if len(args) == 2 and args[1].isdigit():
            with open('cogs/json/profile.js', 'r+') as file:
                profiles = json.load(file)
                user_id = str(ctx.message.author.id)
                if user_id in profiles["profiles"]:
                    user_prof = profiles["profiles"][user_id]
                    game = str(args[0])
                    await self.process_valid_profile(ctx, args, user_prof, game, search)
                else:
                    await ctx.send("Я не нашел ваш профиль используйте команду ?gameprofile")
        elif len(args) == 2 and not args[1].isdigit():
            await search.edit(content=f"{args[1]} не является числом")
        elif len(args) != 2:
            await search.edit(
                content=f"Команда должна быть введена с 2 аргументами\n?find_teammate `название игры` `время в часах`")
        else:
            await search.edit(content="Ссылка на игру не действительна")

    async def process_valid_profile(self, ctx, args, user_prof, game, search):
        """! process_valid_profile - Обработка валидного профиля"""
        with open('cogs/json/games.js', 'r+', encoding='utf-8') as file:
            games = json.load(file)
            if game in games["games"]:
                link_game = games["games"][game]
                if db.user_exists(ctx.message.author.id, link_game):
                    await self.handle_existing_user(ctx, args, link_game, search)
                else:
                    await self.handle_new_user(ctx, args, user_prof, link_game, search)
            else:
                await ctx.send("Не нашел такой игры")

    async def handle_existing_user(self, ctx, args, game_link, search):
        """! handle_existing_user - Обработка существующего пользователя"""
        exit_time = str(db.get_exit_time(ctx.message.author.id))
        await search.edit(content=f"Вы уже стоите в очереди на эту игру до {exit_time[2:-3]}")
        await self.send_ready_gamers(ctx, args, game_link, search)

    async def handle_new_user(self, ctx, args, prof_link, game_link, search):
        """! handle_new_user - Обработка нового пользователя"""
        time = int(args[1])
        exit_time = str((datetime.now() + timedelta(hours=time)).strftime("%H:%M"))
        db.add_gamer(ctx.message.author.id, prof_link, game_link, exit_time,
                     str((datetime.now() + timedelta(hours=time))))
        await TeammateCog.send_ready_gamers(self, ctx, args, game_link, search)

    async def send_ready_gamers(self, ctx, args, game_link, search):
        """! send_ready_gamers - Отправка готовых игроков"""
        gamers = db.get_gamers(game_link)

        if gamers is not None:
            new_gamers = self.filter_and_update_gamers(gamers, ctx.message.author.id)

        if len(new_gamers) > 0:
            gamers = "".join(new_gamers)
            em = discord.Embed(title="Свободные игроки для вашей игры", description=gamers,
                               color=discord.Colour.random())
            await ctx.send(embed=em)
        else:
            await search.edit(content="В данный момент нет игроков на эту игру")

    def filter_and_update_gamers(self, gamers, main_user):
        """! filter_and_update_gamers - Фильтрация и обновление игроков"""
        new_gamers = []

        for user in gamers:
            user = db.remove_special_characters(str(user))

            exit_time2 = str(db.get_whole_time(user))
            datetime_object = datetime.strptime(exit_time2[2:-6], "%Y-%m-%d %H:%M:%S.%f")
            if int(user) != int(main_user):
                if datetime.now() > datetime_object:
                    db.delete_user(user)
                else:
                    exit_time1 = str(db.get_exit_time(user))
                    stroke = f"<@{user}> свободен до `{exit_time1[2:-3]}`\n"
                    new_gamers.append(stroke)

        return new_gamers

    @commands.command(brief="Create or get game profile")
    async def gameprofile(self, ctx, *args):
        user_id = str(ctx.message.author.id)
        with open('cogs/json/profile.js', 'r+') as file:
            try:
                profiles = json.load(file)
            except json.JSONDecodeError:
                profiles = {"profiles": {}}
            if user_id in profiles["profiles"]:
                em = discord.Embed(title="Ваш профиль", description=profiles["profiles"][user_id],
                                   color=discord.Colour.random())
                em.set_thumbnail(url=ctx.author.avatar.url)
                await ctx.send(f"{ctx.author.mention}", embed=em)
            else:
                if len(args) == 0:
                    await ctx.send("Вы не ввели ссылку на профиль.")
                else:
                    link = args[0]
                    if re.match(r'^https://steamcommunity.com/(id|profiles)/', link):
                        profiles["profiles"][user_id] = link
                        file.seek(0)
                        json.dump(profiles, file, ensure_ascii=False)
                        await ctx.send(f"Создал профиль: {link}")
                    else:
                        await ctx.send(
                            "Ссылка на профиль должна начинаться с `https://steamcommunity.com/id/` или `https://steamcommunity.com/profiles/`.")

    @commands.command(brief="Edit game profile")
    async def editprofile(self, ctx, new_link: str):
        user_id = str(ctx.message.author.id)
        with open('cogs/json/profile.js', 'r+') as file:
            profiles = json.load(file)
            if user_id in profiles:
                profiles[user_id] = new_link
                file.seek(0)
                json.dump(profiles, file, ensure_ascii=False)
                await ctx.send(f"Изменил ссылку: {new_link}")
            else:
                await ctx.send("У вас еще нет профиля.")

    @commands.command(brief="Add a game")
    async def addgame(self, ctx, *args):
        if len(args) < 2:
            await ctx.send("Вы не ввели все необходимые аргументы. Пожалуйста, введите название игры и ссылку.")
            return

        name = args[0]
        link = args[1]

        response = requests.get(link, allow_redirects=False)
        if response.status_code == 200 and response.url != "https://store.steampowered.com/":
            with open('cogs/json/games.js', 'r+', encoding='utf-8') as file:
                try:
                    games = json.load(file)
                except json.JSONDecodeError:
                    games = {"games": {}}

                if name in games:
                    await ctx.send("Игра с таким названием уже существует.")
                else:
                    games["games"][name] = link
                    file.seek(0)
                    json.dump(games, file, ensure_ascii=False)
                    await ctx.send(f"Игра {name} ссылка: {link}")
        else:
            await ctx.send("Игра не найдена. Пожалуйста, проверьте ссылку.")


async def setup(bot):
    await bot.add_cog(TeammateCog(bot))
