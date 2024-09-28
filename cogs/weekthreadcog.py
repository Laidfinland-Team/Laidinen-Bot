from __init__ import *


import pytz
import time

from datetime import datetime, timedelta, timezone

DB_DIR = r"light_databases\week_thread.json"






# ID категории форумов и эмодзи для голосования
FORUM_CATEGORY = 123456789012345678  # ID категории форумов
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
        self.top_threads: dict = self.archive["top_threads"] if "top_threads" in self.archive else {}
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
        await paginator.paginate()

    @tasks.loop(hours=1)  # Проверка времени каждый час
    async def hourly_check(self):
        

        """Проверяет каждый час, не наступило ли воскресенье для обновления треда недели."""
        now = datetime.now(jerusalem_tz)
        info(f"WeekThread date was checked")
        
        last_sunday = now - timedelta(days=now.weekday() + 1)

        # Проверяем, наступило ли воскресенье (если это воскресенье, в 23:59 обновляем)
        if now.weekday() == 6 and self.get_last_wt_date().day != now.day:
            weekly_threads = [self.top_threads[t] for t in self.top_threads if datetime.astimezone(datetime.strptime(self.top_threads[t]['created_at'], r"%Y-%m-%d %H:%M:%S"), jerusalem_tz) >= last_sunday]
            
            # Если есть треды, выбираем 3 с наибольшим количеством реакций
            if weekly_threads:
                top_threads = sorted(weekly_threads, key=lambda x: weekly_threads[weekly_threads.index(x)]['reaction_count']['reaction_count'], reverse=True)[:3]
                await self.choose_thread_of_the_week(None, top_threads)
            
            

    async def update_threads_top(self):
        """Выбирает тред недели и обновляет embed сообщение."""
        now = datetime.now(jerusalem_tz)
        last_sunday = now - timedelta(days=now.weekday() + 1)
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
                await self.embed_message.edit(embed=embed)
            
            
        else:
            info("Нет тредов для выбора на этой неделе.")
        
        
    @commands.command()
    @is_hellcat()
    async def ctow(self, ctx):
        await self.choose_thread_of_the_week(ctx)
          
    @commands.command()
    @is_hellcat()
    async def choose_thread_of_the_week(self, ctx: Ctx, top_threads=None):
        start_time = 0
        end_time = 0
        now = datetime.now(jerusalem_tz)
        last_sunday = now - timedelta(days=now.weekday() + 1)

        weekly_threads = [self.top_threads[t] for t in self.top_threads if datetime.astimezone(datetime.strptime(self.top_threads[t]['created_at'], r"%Y-%m-%d %H:%M:%S"), jerusalem_tz) >= last_sunday]
        
        if weekly_threads:
            if not top_threads:
                top_threads = sorted(weekly_threads, key=lambda x: weekly_threads[weekly_threads.index(x)]['reaction_count'], reverse=True)[:3]
        
            author_avatar_url = self.bot.get_user(top_threads[0]['author_id']).avatar.url
            
            async def main():
                start_time = time.perf_counter()
                thread_text = [message async for message in self.bot.get_channel(top_threads[0]['id']).history(limit=10000)][-1].content

                embed: discord.Embed = self.week_embed.add_field(name=f"{top_threads[0]['title']}", value=f"{thread_text}\n\n\n{top_threads[0]['url']}\n-# с {top_threads[0]['reaction_count']} {EMOJI}!")
                embed = embed.set_author(name=f"{top_threads[0]['author']}", icon_url=author_avatar_url)
                
                await self.week_thread_message.edit(content='🏆', embed=embed)
                
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
            
    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload: discord.RawReactionActionEvent):
        """Обрабатывает добавление реакции на сообщения в тредах форума."""
        
        if payload.emoji.name != EMOJI:
            return
        
        
        
        
        
        thread = self.bot.get_channel(payload.channel_id)
        if isinstance(thread, discord.Thread):
            message = await thread.fetch_message(payload.message_id)
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
                
                if thread.id not in self.archive["top_threads"]:
                    print(f"Добавляю новый тред: {thread_data}")
                    self.top_threads[str(thread.id)] = thread_data
                    self.archive["top_threads"][str(thread.id)] = thread_data
                    self.save_archive()
                else:
                    # Проверка: если количество реакций изменилось, обновляем
                    if self.archive["top_threads"][thread.id]['reaction_count'] != thread_data['reaction_count']:
                        print(f"Обновляю тред {thread.id}: старая реакция {self.archive['top_threads'][thread.id]['reaction_count']}, новая реакция {thread_data['reaction_count']}")
                        self.archive["top_threads"][thread.id]['reaction_count'] = thread_data['reaction_count']
                        self.top_threads[thread.id]['reaction_count'] = thread_data['reaction_count']
                        self.save_archive()


                await self.update_threads_top()
    
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
        last_date = max(self.archive.keys())
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