from __init__ import *


import pytz
import time
import copy

from datetime import datetime, timedelta, timezone

DB_DIR = r"light_databases\week_thread.json"





WEEK_AUTHOR_ROLE = 1290267074945486868
# ID категории форумов и эмодзи для голосования
FORUM_CATEGORY = 1180846730602889236  # ID категории форумов 
EMOJI = "🏅"  # Эмодзи для голосования за тред

EMBED_MESSAGE_LINK = "https://discord.com/channels/1156871394173407283/1285119138737557514/1288417937501323314"
WEEK_THREAD_MESSAGE_LINK = "https://discord.com/channels/1156871394173407283/1285119138737557514/1288549934383235104"

class WeekThreadCog(commands.Cog):
    week_embed = discord.Embed(
        title="Лучший тред этой недели!",
        color=discord.Color.yellow()
    )
    
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.embed_message: discord.Message = None
        self.week_thread_message: discord.Message = None
        self.archive = self.load_archive()
        self.top_threads: dict = copy.deepcopy(self.archive["top_threads"]) if "top_threads" in self.archive else {}
          # Запуск задачи с проверкой времени каждый час

    @commands.Cog.listener()
    async def on_ready(self):
        info("WeekThread cog is ready")
        self.embed_message: discord.Message = await self.fetch_message_by_link(EMBED_MESSAGE_LINK)
        self.week_thread_message: discord.Message = await self.fetch_message_by_link(WEEK_THREAD_MESSAGE_LINK)
        self.hourly_check.start()
        
    @commands.command()
    async def pt(self, ctx):
        await self.popular_threads(ctx)
            
    @commands.command()
    async def popular_threads(self, ctx: Ctx):
        """Выводит полный список самых популярных тредов недели с пагинацией."""
        if not self.top_threads:
            await ctx.send("Нет популярных тредов на этой неделе :(")
            return
        last_sunday = datetime.now(jerusalem_tz) - timedelta(days=datetime.now(jerusalem_tz).weekday() + 1)
        weekly_threads = {
            t_id: self.top_threads[t_id] for t_id in self.top_threads
            if datetime.astimezone(datetime.strptime(self.top_threads[t_id]['created_at'], r"%Y-%m-%d %H:%M:%S"), jerusalem_tz) >= last_sunday
        }

        # Разбиваем список тредов на страницы по 10 тредов на каждой
        pages = Paginator.prepare_for_paginate(weekly_threads, "Реакции: {} | [Перейти к треду]({})", ['reaction_count', 'url'])

        # Генератор полей для embed
        def field_generator(thread):
            name = f"{thread['reaction_count']} {EMOJI}"
            value = f" [{thread['title']}]({thread['url']})"
            return name, value

        # Используем Paginator для вывода страниц
        paginator = Paginator(ctx, pages, field_generator)
        if pages:
            await paginator.paginate()
        else:
            await ctx.reply("Нет популярных тредов на этой неделе :(")

    @tasks.loop(hours=1)  # Проверка времени каждый час
    async def hourly_check(self):
        

        """Проверяет каждый час, не наступило ли воскресенье для обновления треда недели."""
        now = datetime.now(jerusalem_tz)
        info(f"WeekThread date was checked")
        
        last_sunday = now - timedelta(days=now.weekday() + 1)

        # Проверяем, наступило ли воскресенье (если это воскресенье, в 23:59 обновляем)
        if now.weekday() == 6 and self.get_last_wt_date().day != now.day:
            await self.clear_week_thread(False)
            await self.update_threads_top(False)
            
            # Если есть треды, выбираем 3 с наибольшим количеством реакций
        else:
            weekly_threads = [self.top_threads[t] for t in self.top_threads if datetime.astimezone(datetime.strptime(self.top_threads[t]['created_at'], r"%Y-%m-%d %H:%M:%S"), jerusalem_tz) >= last_sunday]
            if weekly_threads:
                top_threads = sorted(weekly_threads, key=lambda x: weekly_threads[weekly_threads.index(x)]['reaction_count'], reverse=True)[:3]
                await self.choose_thread_of_the_week(False, top_threads)
    
    
    @commands.command()
    @is_hellcat()
    async def clear_wt(self, ctx):
        await self.clear_week_thread(ctx)
    
    @commands.command()
    @is_hellcat()
    async def clear_week_thread(self, ctx: Ctx):
        """Очищает сообщение с тредом недели."""
        if self.week_thread_message:
            embed = self.week_embed.copy()
            embed.description = "Голосуйте за тред недели на форумах с помощью реакции 🏅!"
            await self.week_thread_message.edit(content="🏆", embed=embed)
        if ctx:
            await ctx.reply("Тред недели успешно очищен!")
            
    @commands.command()
    @is_hellcat()
    async def utt(self, ctx):
        await self.update_threads_top(ctx)
            
           
    @commands.command()
    @is_hellcat()
    async def update_threads_top(self, ctx: Ctx = None):
        """Выбирает тред недели и обновляет embed сообщение."""
        now = datetime.now(jerusalem_tz)
        last_sunday = datetime.now(jerusalem_tz) - timedelta(days=datetime.now(jerusalem_tz).weekday() + 1)
        last_sunday = last_sunday.replace(hour=23, minute=59, second=59)

        # Отфильтровываем треды, созданные на этой неделе
        weekly_threads = []
        for t in self.top_threads:
            created_at = datetime.strptime(self.top_threads[t]['created_at'], r"%Y-%m-%d %H:%M:%S")
            created_at = created_at.astimezone(jerusalem_tz)
            if created_at >= last_sunday:
                weekly_threads.append(self.top_threads[t])
                
        if weekly_threads:
            top_threads = sorted(weekly_threads, key=lambda x: weekly_threads[weekly_threads.index(x)]['reaction_count'], reverse=True)[:3]

            # Создаем embed
            embed = discord.Embed(
                title="Треды этой недели",
                description="3 самых популярных треда, созданных на форуме на этой неделе",
                color=discord.Color.blue()
            )

            for idx, thread in enumerate(top_threads, 1):
                embed.add_field(
                    name=f"Тред #{idx}: {thread['title']}",
                    value=f"Реакции: {thread['reaction_count']} | [Перейти к треду]({thread['url']})"
                )

            # Отправляем embed или обновляем его
            if self.embed_message:
                await self.embed_message.edit(embed=embed, content="🏅")
                if ctx:
                    if ctx.message:
                        await ctx.reply("Треды недели успешно обновлены!")
            
        else:
            info("No threads to choose from this week")
            if ctx:
                if ctx.message:
                    await ctx.reply("Нет тредов для выбора на этой неделе.")
        
        
    @commands.command()
    @is_hellcat()
    async def ctow(self, ctx):
        await self.choose_thread_of_the_week(ctx)
          
    @commands.command()
    @is_hellcat()
    async def choose_thread_of_the_week(self, ctx: Ctx, top_threads=None):
        now = datetime.now(jerusalem_tz)
        last_sunday = now - timedelta(days=now.weekday() + 1)

        weekly_threads = [self.top_threads[t] for t in self.top_threads if datetime.astimezone(datetime.strptime(self.top_threads[t]['created_at'], r"%Y-%m-%d %H:%M:%S"), jerusalem_tz) >= last_sunday]
        
        if weekly_threads:
            if not top_threads:
                top_threads = sorted(weekly_threads, key=lambda x: weekly_threads[weekly_threads.index(x)]['reaction_count'], reverse=True)[:3]

            guild = self.bot.get_guild(GUILD_ID)
            author: discord.Member = guild.get_member(top_threads[0]['author_id'])
            author_avatar_url = author.avatar.url
            
            async def main():
                start_time = time.perf_counter()
                thread_text = [message async for message in self.bot.get_channel(top_threads[0]['id']).history(limit=10000)][-1].content

                embed: discord.Embed = copy.deepcopy(self.week_embed)
                embed.add_field(name=f"{top_threads[0]['title']}", value=f"{thread_text[:1024-150]}{'...' if len(thread_text) > 1024-90 else '' }\n\n\n{top_threads[0]['url']}\n-# с {top_threads[0]['reaction_count']} {EMOJI}!")
                embed = embed.set_author(name=f"{top_threads[0]['author']}", icon_url=author_avatar_url)
                
                
                
                await self.week_thread_message.edit(content='🏆', embed=embed)
                role = guild.get_role(WEEK_AUTHOR_ROLE)
                if role.members:
                    await role.members[0].remove_roles(role)
                await author.add_roles(role)
                
                end_time = time.perf_counter()
                elapsed_time = end_time - start_time
                info(f"Thread of the week was chosen in {elapsed_time:.2f} seconds")
                
                return elapsed_time

            
            if ctx:
                async with ctx.typing():
                    elapsed_time = await main()
                await ctx.message.reply(f"Тред недели успешно выбран!\n-# за {elapsed_time:.2f} секунды")
            else:
                await main()
        else:
            if ctx:
                await ctx.reply("Нет тредов для выбора на этой неделе.")
            info("No threads to choose from this week")
            
    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload: discord.RawReactionActionEvent):
        """Обрабатывает добавление реакции на сообщения в тредах форума."""
        
        if payload.emoji.name != EMOJI:
            return
        
        thread = self.bot.get_channel(payload.channel_id)
        message = await thread.fetch_message(payload.message_id)
        
        if thread.category_id != FORUM_CATEGORY:
            return
        
        
        
        
        if isinstance(thread, discord.Thread):
            thread_data = {
                'id': thread.id,
                'author': thread.owner.name,
                'author_id': thread.owner.id,
                'title': thread.name,
                'url': message.jump_url,
                'reaction_count': sum([(r.count if r.emoji == EMOJI else 0) for r in message.reactions]),
                'created_at': thread.created_at.strftime(r"%Y-%m-%d %H:%M:%S")
            }

            # Проверяем, был ли тред создан на этой неделе
            now = datetime.now(jerusalem_tz)
            if (now - thread.created_at).days <= 7:
                
                if str(thread.id) not in self.archive["top_threads"] and thread_data['reaction_count'] > 0:
                    info(f"Thread added to archive: {thread_data["id"]}")
                    self.top_threads[str(thread.id)] = thread_data
                    self.archive["top_threads"][str(thread.id)] = thread_data
                    self.save_archive()
                else:
                    # Проверка: если количество реакций изменилось, обновляем
                    if thread_data['reaction_count'] == 0:
                        info(f"Thread {thread.id} has no reactions, removing from archive")
                        self.archive["top_threads"].pop(str(thread.id))
                        self.top_threads.pop(str(thread.id))
                        self.save_archive()
                    elif self.archive["top_threads"][str(thread.id)]['reaction_count'] != thread_data['reaction_count']:
                        info(f"Updating thread {thread.id}: old reactions count: {self.archive['top_threads'][str(thread.id)]['reaction_count']}, new reaction count: {thread_data['reaction_count']}")
                        self.archive["top_threads"][str(thread.id)]['reaction_count'] = thread_data['reaction_count']
                        self.top_threads[str(thread.id)]['reaction_count'] = thread_data['reaction_count']
                        self.save_archive()


                await self.update_threads_top(False)
    
    @commands.Cog.listener()
    async def on_raw_reaction_remove(self, payload: discord.RawReactionActionEvent):
        await self.on_raw_reaction_add(payload)
                   
    def load_archive(self):
        """Загружает архив тредов недели из JSON файла, удаляя дубликаты."""
        try:
            with open(DB_DIR, "r", encoding="utf-8") as f:
                data = json.load(f)
                if "top_threads" not in data:
                    data["top_threads"] = {}
                return data
        except FileNotFoundError:
            return {"top_threads": {}}
        except json.JSONDecodeError:
            # Если файл пуст или содержит некорректные данные
            return {"top_threads": {}}



    def save_archive(self):
        """Сохраняет архив тредов недели в JSON файл."""
        with open(DB_DIR, "w", encoding="utf-8") as f:
            
            l = [t for t in self.archive["top_threads"]]
            for t in l:
                if l.count(t) > 1:
                    self.archive["top_threads"].pop(t).pop(t)
            
            json.dump(self.archive, f, ensure_ascii=False, indent=4)
            
    
    def get_last_wt_date(self):
        """Возвращает дату последнего треда недели из архива."""
        if not self.archive:
            return None
        # Получаем последнюю дату из архива
        last_date = max(v['created_at'] for v in self.archive['top_threads'].values())
        return datetime.fromisoformat(last_date)

    async def fetch_message_by_link(self, link):
        """Получает сообщение по ссылке."""
        try:
            parts = link.split('/')
            guild_id = int(parts[4])
            channel_id = int(parts[5])
            message_id = int(parts[6])
            guild = self.bot.get_guild(guild_id)
            channel = guild.get_channel(channel_id)
            message = await channel.fetch_message(message_id)
            return message
        except (IndexError, ValueError, AttributeError):
            return None

        
async def setup(bot):
    await bot.add_cog(WeekThreadCog(bot))