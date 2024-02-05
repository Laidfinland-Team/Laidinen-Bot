import random

from __init__ import *

# Словарик ответов
opinion = ["Ну я понимаю такое увлечение, но не особо, лучше на турники сгоняй", "Ну слушай это адекватная тема",
           "Поплачь", "Я про это даже видосик снимал, ща скину https://youtu.be/dQw4w9WgXcQ?si=C49WJJW3R2Em1NOu"]


class Opinion(commands.Cog, name="Opinion command"):

    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        """! on_ready - Событие, которое вызывается при готовности кога
        @return Сообщение о готовности кога"""
        info(f"TeammateCog cog is ready")

    @commands.command(brief="Высказать мнение")
    async def opinion(self, ctx, *args):
        if len(args) >= 1:
            await ctx.send(random.choice(opinion))
        else:
            await ctx.send("Я конечно все понимаю, но высказать мнение о ситуации которую я не знаю не могу. :(")


async def setup(bot):
    await bot.add_cog(Opinion(bot))
