import sys, os
from typing import Any; #sys.path.insert(0, os.path.join(os.getcwd(), ''))

from __init__ import *
import discord



class TheBestChannelCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        info("TheBestChannelCog cog is ready")
        
    @commands.command()
    async def thebestchannel(self, ctx):
        file = discord.File(os.getcwd() +  "\\botfiles\\banner.jpg", filename="banner.jpg")
        
        embed = discord.Embed(title="The Best Channel", description="# Зацени самый чёткий канальчик про отношения!", url="https://www.youtube.com/@Laidfin", color=discord.Color.pink())
        embed.set_image(url="attachment://banner.jpg")
        embed.add_field(name="Ссылочка", value="https://www.youtube.com/@Laidfin", inline=False)
        try:
            await ctx.send(file=file, embed=embed)
        except:
            error(e)
            info("Приносим свои извинения, но произошла ошибка при отправке сообщения. Попробуйте позже.")
        
async def setup(bot):
    await bot.add_cog(TheBestChannelCog(bot))