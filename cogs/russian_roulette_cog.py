import random
from datetime import timedelta

from __init__ import *

TIMEOUT = 20  ## Время таймаута кнопок
MUTE = timedelta(minutes=15)  # Время мута после смерти
DIED_CHANCE = 5  # Пиши только делитель => 1 / DIED_CHANCE ## Шанс умереть


class Confirm(discord.ui.View):
    success_messages = ["Сегодня тебе везёт :)", "Ты выжил", "Ты победил", "**Удача исчерпана**",
                        "Сходи в лотерею, сегодня твой день", "у тебя всё получится 🌹"]  ## Сообщения при осечке
    failure_messages = ["БУМ и ты отлетаешь!", "**YOU DIED**", "Пока-пока!)", "Да ты снайпер! Точно в цель)",
                        "Ну, в любви уже не повезёт", "Удачный косплей на Кобейна",
                        "Упс, в барабане оказалось больше патронов"]  ## Сообщения при выстреле

    ## Эмбеды для сообщений при осечке
    success_embed = discord.Embed(
        title="ПУСТО",
        color=discord.Color.lighter_grey()
    )

    ## Эмбеды для сообщений при выстреле
    failure_embed = discord.Embed(
        title="ВЫСТРЕЛ!!!",
        color=discord.Color.red()
    )

    def __init__(self, ctx):
        super().__init__(timeout=TIMEOUT)
        self.value = None
        self.died = False
        self.ctx = ctx

    async def interaction_check(self, interaction: discord.Interaction):
        return interaction.user.id == self.ctx.message.author.id

    @discord.ui.button(label='Спуск', style=discord.ButtonStyle.red)
    async def shoot(self, interaction: discord.Interaction, button: discord.ui.Button):

        '''! shoot - Функция для обработки нажатия кнопки "Спуск"'''

        if not await Confirm.interaction_check(self, interaction):
            return
        await interaction.response.defer()
        if random.randint(0, DIED_CHANCE):
            await self.ctx.send(Confirm.success_messages[random.randint(0, len(Confirm.success_messages)) - 1])
            await interaction.message.edit(embed=Confirm.success_embed)
            self.died = False
        else:
            await self.ctx.send(Confirm.failure_messages[random.randint(0, len(Confirm.failure_messages)) - 1])
            await interaction.message.edit(embed=Confirm.failure_embed)
            self.died = True
        self.value = True
        self.stop()
        await interaction.message.edit(view=None)

    @discord.ui.button(label='Зассал', style=discord.ButtonStyle.gray)
    async def cancel(self, interaction: discord.Interaction, button: discord.ui.Button):

        '''! cancel - Функция для обработки нажатия кнопки "Зассал"'''
        await interaction.response.defer()
        self.value = False
        await self.ctx.message.delete()

        await interaction.message.delete()
        self.stop()
        await interaction.message.edit(view=None)


class RussianRouletteCog(commands.Cog, name="Games"):
    """! Команды для игры в русскую рулетку"""

    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):

        """! Событие, которое вызывается при готовности кога"""

        info("GamesCog cog is ready")

    @commands.command(brief="Русская рулетка")
    async def russian_roulette(self, ctx, member: discord.Member = None):

        """! Команда для игры в русскую рулетку"""

        if member:
            embed = discord.Embed(title=f"Тебе предложили сыграть в Русскую рулетку",
                                  description=f"Что бы сыграть введи команду `{PREFIX}russian_roulette`\nУ тебя лишь одна жизнь.\nЕсли погибнешь получишь мут на {MUTE} минут",
                                  color=discord.Color.red())
            embed.set_footer(text=f"Игра с {ctx.message.author.name}")

            await ctx.send(content=f"<@{member.id}>", embed=embed)
            await ctx.send(content=f"https://media1.tenor.com/m/lm8iTuh1lRIAAAAd/gun-weapon.gif")

        else:
            embed = discord.Embed(title="Русская Рулетка",
                                  description=f"У тебя лишь одна жизнь.\nЕсли погибнешь получишь мут на {MUTE} минут",
                                  color=discord.Color.red())

            view = Confirm(ctx)

            self.message_with_buttons = await ctx.send(embed=embed, view=view)
            await view.wait()

            if view.value is None:
                info(ctx.channel.name + ': Russian Roulette: Timed out')
                await self.message_with_buttons.edit(view=None)
                await ctx.send('Время вышло сосунок...')

            elif view.value:
                info(ctx.channel.name + ': Russian Roulette:  Confirmed')

            else:
                info(ctx.channel.name + ': Russian Roulette:  Cancelled')

            if view.died:
                try:
                    await ctx.author.timeout(MUTE)
                    info(ctx.channel.name + ': Russian Roulette:  Muted')
                except Exception as e:
                    error(f"Timeout error: {e}")


async def setup(bot):
    await bot.add_cog(RussianRouletteCog(bot))
