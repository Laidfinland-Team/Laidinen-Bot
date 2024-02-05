import random

from __init__ import *

advices = ["Банан большой но кожура еще больше", "И это пройдет, и твоя бывшая пройдет, и заваленный экз пройдет",
           "Включи русского постпанка и откиси"]


class AdviceCog(commands.Cog, name="Advice commands"):

    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        """! on_ready - Событие, которое вызывается при готовности кога
        @return Сообщение о готовности кога"""

        info(f"Advice cog is ready")

    @commands.command(brief="Попросить совет")
    async def advice(self, ctx, *args):
        if len(args) == 0:
            await ctx.send("Интересная ситуация, а можно подробнее?")
        else:
            await ctx.send(random.choice(advices))


async def setup(bot):
    await bot.add_cog(AdviceCog(bot))
