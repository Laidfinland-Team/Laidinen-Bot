
from __init__ import *


class LinksCog(commands.Cog, name="Links commands"):
    """! Команды с ссылками на соцсети Артёма"""

    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        """! on_ready - Событие, которое вызывается при готовности кога
        @return Сообщение о готовности кога"""

        info(f"Links cog is ready")

    @commands.command(brief="Ссылки на соц сети")
    async def links(self, ctx):
        embed = discord.Embed(title="Ссылки на медиа",
                              description="**[YouTube](https://www.youtube.com/@Laidfin)**\n**[VK](https://vk.com/laidfine)**\n**[Telegram](https://t.me/oleglatunin)**\n**[Boosty](https://boosty.to/laid)**",color=discord.Color.red())
        await ctx.send(embed=embed)


async def setup(bot):
    await bot.add_cog(LinksCog(bot))
