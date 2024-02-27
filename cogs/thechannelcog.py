import sys, os
from typing import Any; #sys.path.insert(0, os.path.join(os.getcwd(), ''))

from __init__ import *
import discord

class TheChannelCog(commands.Cog, name="Channel commands"):
    
    """! Команды про канал"""
    
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        
        """! on_ready - Событие, которое вызывается при готовности кога
        @return Сообщение о готовности кога"""
        
        info("TheBestChannel cog is ready")
        
        
    @commands.command(brief="Лучший канал про отношения")
    async def thebestchannel(self, ctx):
        
        """! thebestchannel - Команда, которая выводит информацию о канале
        @param ctx - Контекст команды
        @return Discord embed с информацией о канале
        """
        
        file = discord.File(os.getcwd() +  "\\botfiles\\banner.jpg", filename="banner.jpg")
        
        embed = discord.Embed(title="The Best Channel", description="# Зацени самый чёткий канальчик про отношения!", url="https://www.youtube.com/@Laidfin", color=MAIN_COLOR)
        embed.set_image(url="attachment://banner.jpg")
        embed.add_field(name="Ссылочка", value="https://www.youtube.com/@Laidfin", inline=False)
        
        await ctx.send(file=file, embed=embed)
        
        
async def setup(bot):
    await bot.add_cog(TheChannelCog(bot))