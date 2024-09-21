from __init__ import *

# ID категории, в которой будут проверяться форумы
FORUM_CATEGORY = 1286305275480903741
# Эмоджи, который будет использоваться для отслеживания
EMOJI = "<:test:1286987598841253942>"

# Путь к файлу базы данных
DB_DIR = r"light_database\week_thread.json"

class WeekthreadCog(commands.Cog):
    def __init__(self, bot):
        self.bot: discord.Client = bot
        self.main_loop.start() # Запуск основного цикла

    @tasks.loop(hours=1.0)
    async def main_loop(self):
        # Проходимся по всем форумам в указанной категории
        for i in self.bot.get_channel(FORUM_CATEGORY).forums:
            for j in i.threads:
                message = await j.fetch_message(j.id)
                for n in message.reactions:
                    print(n.emoji)
                    # Проверяем, является ли реакция указанным эмоджи
                    if str(n.emoji) == EMOJI:
                        # Если форума еще нет в базе данных, добавляем его
                        if not await self.check_thread(message):
                            await self.add_thread(j.id, str(n.emoji ), n.count)

    async def check_thread(self, message):
        # Проверяем, есть ли форум в базе данных
        with open(DB_DIR, "r") as f:
            print(f)
            for k, i in json.loads(f):
                if k == message.id:
                    return True
        return False

    async def add_thread(self, id, emoji, count):
        # Добавляем новый форум в базу данных
        with open(DB_DIR, "r") as f:
            threads = json.loads(f)
        threads[id] = [emoji, count]
        with open(DB_DIR, "w") as f:
            json.dump(threads, f)
        print(f"Новый форум добавлен: {id} - {emoji} - {count}")