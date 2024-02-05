import random

from __init__ import *

replies = ["Ну у user сразу видно что iq больше а значит он прав",
           "Канеш user местами серьезен шо ебало трещит, но в целом тему говорит",
           "Ребят хуйней маетесь, идите посмотрите поней и отвлекитесь"]


class WhoIsRightCog(commands.Cog, name="WIR commands"):

    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        """! on_ready - Событие, которое вызывается при готовности кога
        @return Сообщение о готовности кога"""

        info(f"WIR cog is ready")

    @commands.command(brief="Кто прав")
    async def whoright(self, ctx, user1: discord.Member, user2: discord.Member):
        if user1 != user2:
            users = [user1.id, user2.id]
            reply = random.choice(replies)
            reply = reply.replace("user", "<@" + str(random.choice(users)) + ">")
            await ctx.send(reply)
        else:
            await ctx.send("Пользователи должны быть разными")


async def setup(bot):
    await bot.add_cog(WhoIsRightCog(bot))
