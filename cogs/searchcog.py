from __init__ import *
from discord.ext import commands
import discord
import asyncio
import statistics
import time
from discord.errors import NotFound, HTTPException, Forbidden
import numpy as np

TIMEOUT_FOR_PAGES = 60*3

class SearchCog(commands.Cog):
    def __init__(self, bot):
        self.bot: discord.Client = bot
        self.MAX_PER_PAGE = 6000
        self.MAX_FIELDS = 20
        self.message_cache = {}

    @commands.Cog.listener()
    async def on_ready(self):
        info("Search cog is ready")
    
    @commands.command()
    async def sbr(self, ctx: Ctx, limit: str, channel: str = None, percentile: str = "90%", sort_type: str = "total"):
        await self.search_by_reactions(ctx, limit, channel, percentile, sort_type)
        
    @commands.command()
    async def search_by_reactions(self, ctx: Ctx, limit: str, channel: str = None, percentile: str = "90%", sort_type: str = "total"):
        info("search_by_reactions was called")
        start_time = time.perf_counter()
        async with ctx.typing():
            guild = ctx.guild
            limit = int(limit)
            sort_type = sort_type.lower()

            if channel is None:
                channels = guild.text_channels
            else:
                channel2 = "".join([str(tryParseInt(l)) for l in channel if type(tryParseInt(l)) is int])
                channels = [guild.get_channel(int(channel2))]

            all_reactions = []
            messages_data = []

            for c in channels:
                async for message in c.history(limit=limit):
                    if message.reactions:
                        reactions_count = sum([reaction.count for reaction in message.reactions])
                        max_reaction = max([reaction.count for reaction in message.reactions])

                        all_reactions.append(reactions_count)
                        messages_data.append({
                            "url": message.jump_url,
                            "total_reactions": reactions_count,
                            "max_reactions": max_reaction,
                        })

                    await asyncio.sleep(0.0001)

            if not messages_data:
                await ctx.send("Сообщения с реакциями не найдены.")
                return

            # Определение порога
            if percentile.endswith('%'):
                percentile_value = float(percentile[:-1])
                if sort_type == "max":
                    threshold = np.percentile([m["max_reactions"] for m in messages_data], percentile_value)
                else:
                    threshold = np.percentile(all_reactions, percentile_value)
            elif percentile.lower() == "median":
                if sort_type == "max":
                    threshold = statistics.median([m["max_reactions"] for m in messages_data])
                else:
                    threshold = statistics.median(all_reactions)
            else:
                threshold = int(percentile)

            # Фильтрация сообщений
            if sort_type == "max":
                most_popular = [m for m in messages_data if m["max_reactions"] >= threshold]
            else:
                most_popular = [m for m in messages_data if m["total_reactions"] >= threshold]

            # Сортировка сообщений
            most_popular = sorted(most_popular, key=lambda x: x[sort_type + "_reactions"], reverse=True)

            # Разбиение на страницы
            pages = [most_popular[i:i + self.MAX_FIELDS] for i in range(0, len(most_popular), self.MAX_FIELDS)]

            if not pages:
                await ctx.send("Нет сообщений, соответствующих порогу.")
                return
            
            end_time = time.perf_counter()
            elapsed_time = end_time - start_time
            await ctx.send(f"**Поиск завершен за {elapsed_time:.2f} секунд.**")

        async def send_page(page_index):
            embed = discord.Embed(
                title=f"Страница {page_index + 1}/{len(pages)}",
                description=f"Порог ({percentile}): {threshold:.2f}. Сообщений на странице: {len(pages[page_index])}",
                color=MAIN_COLOR
            )
            for message_data in pages[page_index]:
                embed.add_field(
                    name=f"Сообщение:\n{message_data['url']}",
                    value=f"Количество реакций: {message_data['total_reactions']}, \nСамая популярная реакция: {message_data['max_reactions']}"
                )

            msg = await ctx.send(embed=embed)
            return msg

        page_index = 0
        msg = await send_page(page_index)
        await msg.add_reaction("⬅️")
        await msg.add_reaction("➡️")

        def check_reaction(reaction, user):
            return user == ctx.author and str(reaction.emoji) in ["⬅️", "➡️"]

        while True:
            try:
                reaction, user = await self.bot.wait_for('reaction_add', timeout=TIMEOUT_FOR_PAGES, check=check_reaction)
                if str(reaction.emoji) == "➡️" and page_index < len(pages) - 1:
                    page_index += 1
                    await msg.delete()
                    msg = await send_page(page_index)
                    await msg.add_reaction("⬅️")
                    await msg.add_reaction("➡️")
                elif str(reaction.emoji) == "⬅️" and page_index > 0:
                    page_index -= 1
                    await msg.delete()
                    msg = await send_page(page_index)
                    await msg.add_reaction("⬅️")
                    await msg.add_reaction("➡️")
            except asyncio.TimeoutError:
                break


async def setup(bot):
    await bot.add_cog(SearchCog(bot))