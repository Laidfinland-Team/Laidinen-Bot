import sys, os; #sys.path.insert(0, os.path.join(os.getcwd(), ''))

from __init__ import *

import itertools
import textwrap
import datetime
import urllib
import random
import typing
import time 
import re

from PIL import Image, ImageDraw, ImageOps, ImageFont
from dataclasses import dataclass
from discord import app_commands
from discord.ext import tasks
from io import BytesIO


def get_special_channel_id():
    with open("cogs/warns/special.txt", "r") as f:
        try:
            return int(f.readline())
        except ValueError:
            error("IpegaCog - cogs/warns/special.txt - incorrect Channel ID")
            return 1

def set_special_channel_id(channel_id: int):
    with open("cogs/warns/special.txt", "w") as f:
        f.write(str(channel_id))

def without_spaces(string):
    return "".join(string.split())


SUBTASKS = ["del", "mute", "unmute", "unwarn", "warn", "ban"]
POSITIVE_TASKS = ["unwarn","warn","unmute", "unban", "patpat", "durov"]
WARN_LIMIT = 3
WARN_TIMEOUT_TIME = 30 # Дни тайм-аута за WARN_LIMIT предупреждений.
WARN_TIMEOUT_STEP = 1 # Время тайм-аута за предупреждения будет разбито на тайм-ауты по столько дней

@dataclass
class FakeMessage():
    """ Класс, позволяющий создать копию discord.Message для обработки отрисовщиком скриншотов """

    content: str = None
    reactions: typing.List[discord.Reaction] = ()
    mentions: typing.List[discord.Member] = ()



class Report():
    """ Класс для создания и отправки сообщения в канал для модераторов """

    def __init__(self, member: typing.Optional[discord.Member]):

        offset = datetime.timedelta(hours=3)
        self.tz = datetime.timezone(offset, name='МСК')


        self.id = random.randint(1, 1000000)
        self.member = member
        self.img_filename = f"{self.id}.png"
        self.img_file = None # discord.File
        self.attachments = [] # discord.File


        self.time = datetime.datetime.now(tz=self.tz).strftime("%d %B - %H:%M")
        self.title = None
        self.desc = ""
        self.color = discord.Colour.random()

    def set_desc(self, name, value):
        self.desc = self.desc + f"\n**{name}:** {value}"

    def set_title(self, title):
        self.title = title

    def __get_main_embed(self):
        embed = discord.Embed(title=self.title, description=self.desc, color=self.color)
        embed.set_image(url=f"attachment://{self.img_filename}")
        return embed

    async def create_img(self, messages):

        TEXT_COLOR = discord.Color.light_embed().to_rgb()
        DATE_COLOR = discord.Color.light_gray().to_rgb()

        FONT_SIZE = 24

        SMALL_FONT = ImageFont.truetype("cogs/warns/NotoSans-Regular.ttf", FONT_SIZE - 10) # Уменьшенный шрифт (дата отправки)
        NORMAL_FONT = ImageFont.truetype("cogs/warns/NotoSans-Regular.ttf", FONT_SIZE) # Обычный шрифт (текст)
        BOLD_FONT = ImageFont.truetype("cogs/warns/NotoSans-Medium.ttf", FONT_SIZE) # Жирный шрифт (никнейм)

        BACKGROUND_COLOR = (54, 57, 63)

        # Контент = аватарка + никнейм + текст + всё остальное, короче всё кроме фона входит в блок контента

        CONTENT_X = 15  # Расстояние от левого края изображения до контента
                        # Изменять для смещения всего содержимого влево/вправо

        CONTENT_Y = 10  # Расстояние от верхнего края изображения до контента
                        # Изменять для смещения всего содержимого вверх/вниз

        DISTANCE_BETWEEN_AVATAR_AND_TEXTBOX = 90 # Расстояние между левым краем аватарки и текстом
        DISTANCE_BETWEEN_NAME_AND_DATE = 5 # Расстояние между никнеймом и датой отправки
        ONE_MESSAGE_HEIGHT = 40 # Высота одного однострочного сообщения

        TEXTBOX_X = CONTENT_X + DISTANCE_BETWEEN_AVATAR_AND_TEXTBOX # Расстояние от левого края изображения до текста
        TEXTBOX_Y = CONTENT_Y - 2 # Минус чтобы выровнять в одну линию текст и аватарку

        for i, message in enumerate(messages): # Вложения на скриншоте игнорируются, на их месте становится надпись [Вложение]
            if message.attachments or message.embeds:
                if len(message.attachments) == 1 or len(message.embeds) == 1:
                    messages = list(messages[:i+1]) + [FakeMessage(content = "[вложение]")] + list(messages[i+1:])
                elif len(message.attachments) > 1 or len(message.embeds) > 1:
                    messages = list(messages[:i+1]) + [FakeMessage(content = "[вложения]")] + list(messages[i+1:])


        height_increase = 40 * (len(messages)) + 5 # На каждое текстовое сообщение в высоту добавляется 40 пикселей + отступ в конце
        img_size = (750, 60 + height_increase) # Размер картинки


        img = Image.new(mode='RGB', size=img_size, color=BACKGROUND_COLOR) # Создание изображения
        img_draw = ImageDraw.Draw(img) # Объект для рисования на изображении


        messages_author = messages[0].author
        date = messages[0].created_at.strftime("%d.%m.%Y %H:%M")
        nickname = messages_author.display_name
        nickname_color = messages_author.color.to_rgb()


        member_avatar = Image.open(BytesIO(await messages_author.display_avatar.with_size(64).read()))
        mask = Image.open("cogs/warns/mask.png").convert('L')
        member_avatar = ImageOps.fit(member_avatar, mask.size, centering = (0.5, 0.5)) # Округливание аватарки


        if nickname_color == discord.Color.default().to_rgb(): # Если цвет ника стандартный
            nickname_color = TEXT_COLOR


        img_draw.text((TEXTBOX_X, TEXTBOX_Y), nickname, nickname_color, font = BOLD_FONT) # рисование никнейма
        #img_draw.text((TEXTBOX_X + (len(without_spaces(nickname)) * (FONT_SIZE - 4)) + nickname.count(" ") * 2, TEXTBOX_Y + 10), date, DATE_COLOR, font = SMALL_FONT) # рисование даты
        img.paste(member_avatar, (CONTENT_X, CONTENT_Y), mask = mask) # рисование аватарки


        previous_position = TEXTBOX_Y - 5 # Позиция по Y предыдущего сообщения. 

        for message in messages:
            message_text = textwrap.fill(message.content, width = 40, replace_whitespace = False)

            for member in message.mentions: # заменяет упоминание на @никнейм
                message_text = re.sub(f"<@{member.id}>", f"@{member.display_name}", message_text)

            strings_amount = len(message_text.splitlines())

            if strings_amount > 1:
                img_size = (img_size[0], img_size[1] + ONE_MESSAGE_HEIGHT * strings_amount - ONE_MESSAGE_HEIGHT - 10)
                old_img = img
                img = Image.new(mode = 'RGB', size = img_size, color = BACKGROUND_COLOR)
                img_draw = ImageDraw.Draw(img)
                img.paste(old_img)

            string_pos = previous_position + ONE_MESSAGE_HEIGHT

            if message.content:

                color = TEXT_COLOR
                if isinstance(message, FakeMessage): 
                    color = DATE_COLOR

                img_draw.multiline_text(xy = (TEXTBOX_X, string_pos), 
                                        text = message_text, 
                                        fill = color, 
                                        font = NORMAL_FONT,
                                        spacing = ONE_MESSAGE_HEIGHT / 3)
                

            previous_position = previous_position + ONE_MESSAGE_HEIGHT * strings_amount


        return img

    async def upload_attachments(self, messages):
        for message in messages:
            self.attachments.extend([discord.File(fp = BytesIO(await a.read()), filename = a.filename) for a in message.attachments])

    def set_image(self, img):
        if img:
            imgb = BytesIO()
            img.save(imgb, format = "PNG")
            imgb.seek(0)
            self.img_file = discord.File(fp = imgb, filename = self.img_filename)

    async def send(self, output_channel):
        main_embed = self.__get_main_embed()
        sub_embeds = []

        if self.attachments:
            for i, a in enumerate(self.attachments):
                e = discord.Embed(description = f"Вложение {i}", color = self.color)
                e.set_image(url = f"attachment://{a.filename}")
                sub_embeds.append(e)
            #sub_embeds.extend([discord.Embed(url = f"attachment://{a.filename}", description = f"Вложение {i}", color = self.color) for i, a in enumerate(self.attachments)])

        report_msg = await output_channel.send(file = self.img_file, embed = main_embed)
        if self.attachments:
            await output_channel.send(embeds = sub_embeds, files = self.attachments)

        return report_msg



class IpegaCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.cog_ready = False
        self.check_warns.start()

    @commands.Cog.listener()
    async def on_ready(self):
        info("IpegaCog is ready")
        cog_ready = True


    @tasks.loop(hours=WARN_TIMEOUT_STEP)
    async def check_warns(self):
        connection = sqlite3.connect("cogs/warns/warns.db")
        cursor = connection.cursor()

        connection.execute(""" CREATE TABLE IF NOT EXISTS users (member_id INTEGER, warns INTEGER, guild_id INTEGER); """)       # имя : кол-во предупреждений : guild_id
        connection.execute(""" CREATE TABLE IF NOT EXISTS banned (member_id INTEGER, banned_for INTEGER, guild_id INTEGER); """) # имя : отбыто дней в бане    : guild_id

        cursor.execute("SELECT member_id, banned_for, guild_id FROM banned")
        banned_list = cursor.fetchall()

        for record in banned_list:
            member_id = record[0]
            banned_for = record[1]
            guild_id = record[2]

            while not self.cog_ready:
                await asyncio.sleep(0.1)
            guild = self.bot.get_guild(guild_id)
            member = await guild.fetch_member(member_id)

            
            if banned_for == WARN_TIMEOUT_TIME:
                await member.timeout(None)
                cursor.execute(f"DELETE FROM banned WHERE member_id={member_id}")
            else:
                cursor.execute(f"DELETE FROM banned WHERE member_id={member_id}")
                cursor.execute(f"INSERT INTO banned (member_id, banned_for) VALUES (?, ?)", (member_id, banned_for + WARN_TIMEOUT_STEP,))
                await member.timeout(datetime.timedelta(hours=WARN_TIMEOUT_STEP), reason=f"До разблокировки осталось {WARN_TIMEOUT_TIME - banned_for} дней.")

        connection.commit()
        connection.close()
        
    @commands.command() # This is a command, like @bot.command()
    @commands.has_permissions(manage_channels=True)
    async def ipega(self, ctx, member: typing.Optional[discord.Member] = None, amount: typing.Optional[int] = 0, subtask: typing.Optional[str] = "del", mute_time: typing.Optional[str] = "10m", reason: typing.Optional[str] = "Не указано"):
        
        is_subtask_positive = subtask in POSITIVE_TASKS # если подкоманда (mute, unmute, ban...) является положительной
                                                        # то сообщение, упомянутое модератором, не будет удалено

        output_channel = await ctx.guild.fetch_channel(get_special_channel_id())

        mentioned_message = None
        if ctx.message.reference:
            mentioned_message = await ctx.fetch_message(ctx.message.reference.message_id) # сообщение, которое было упомянуто
            member = mentioned_message.author # автор упомянотого модератором сообщения

        if subtask not in SUBTASKS:
            reason = subtask
            subtask = "del"

        is_mute_time_correct = re.search(r"^\d+[a-zA-Z]", mute_time) # указано ли время тайм-аута в формате ЧислоЕдиница
        if not is_mute_time_correct and reason == "Не указано":
            reason = mute_time
            mute_time = "10m"

        members = [member]

        one_person_report = member != None
        
        main_report_message = None
        main_report_title = None
        if not one_person_report: # если никакое сообщение или участник не упомянут модератором

            main_report = Report(None)

            imgs = []
            members_references = []
            members = []

            messages = list(reversed([i async for i in ctx.history(limit = amount + 1)]))
            await main_report.upload_attachments(messages)

            for message in messages:
                if message != ctx.message:
                    report = Report(message.author)

                    if message.author not in members:
                        members.append(message.author)
                    if f"<@{message.author.id}>" not in members_references:
                        members_references.append(f"<@{message.author.id}>")

                    img = await report.create_img((message, ))
                    if img:
                        imgs.append(img)

            await ctx.channel.purge(limit = amount + 1, check = lambda msg: msg != ctx.message)


            main_img = Image.new(mode = "RGB", size=(750, sum([img.height for img in imgs])))

            height = 0
            for i, img in enumerate(imgs):
                main_img.paste(img, (0, height))
                height += img.height

            main_report.set_image(main_img)
            main_report.set_title(f"[{report.time}] Танцуют все")
            main_report.set_desc("Участники", " ".join(members_references))
            main_report.set_desc("Команда", subtask)
            main_report.set_desc("Причина", reason)
            main_report.set_desc("Кол-во удалённых сообщений", amount)

            main_report_message = await main_report.send(output_channel = output_channel)
            main_report_title = main_report.title




        for member in members:

            report = Report(member)
            report.set_title(f"[{report.time}] Репорт на {member.name}")
            report.set_desc("Участник", f"<@{member.id}>")
            report.set_desc("Команда", subtask)
            report.set_desc("Причина", reason)


            if one_person_report:
                if not is_subtask_positive:
                    if not mentioned_message:

                        messages_deleted = 0 # счётчик удалённых сообщений
                        messages_to_delete = [] # список сообщений, которые будут удалены

                        async for message in ctx.history(limit=None):
                            if message.author == member and message is not ctx.message: 
                                messages_to_delete.append(message)
                                messages_deleted += 1
                            if messages_deleted == amount:
                                break

                        if messages_to_delete:
                            reversed_messages = list(reversed(messages_to_delete))

                            image = await report.create_img(reversed_messages)
                            await report.upload_attachments(reversed_messages)

                            report.set_image(image)
                            await ctx.channel.delete_messages(messages_to_delete)

                    else:
                        image = await report.create_img([mentioned_message])
                        await report.upload_attachments([mentioned_message])
                        report.set_image(image)
                        amount = 1
                        await mentioned_message.delete()

                    report.set_desc("Кол-во удалённых сообщений", amount)


            match subtask:
                case "warn":
                    connection = sqlite3.connect("cogs/warns/warns.db")
                    cursor = connection.cursor()

                    cursor.execute(f"SELECT member_id, warns FROM users WHERE member_id={member.id}")
                    record = cursor.fetchone()
                    cursor.execute(f"DELETE FROM users WHERE member_id={member.id}")

                    if record: # если запись существует - прибавить предупреждение к ней
                        warns = record[1] + 1
                    else: # иначе - создать новую запись
                        warns = 1

                    report.set_desc("Кол-во предупреждений", f"{warns}/{WARN_LIMIT}") # изменение сведений в репорте
                    await ctx.send(f"Чуваку <@{member.id}> выдано предупреждение ({warns}/{WARN_LIMIT}).")
                    cursor.executemany("INSERT INTO users (member_id, warns, guild_id) VALUES (?, ?, ?)", ((member.id, warns, member.guild.id), ))

                    if warns >= WARN_LIMIT:
                        banned_for = 0

                        cursor.execute(f"DELETE FROM users WHERE member_id={member.id}") # снять с учёта кол-ва предупреждений
                        cursor.execute("INSERT INTO banned (member_id, banned_for, guild_id) VALUES (?, ?, ?)", (member.id, banned_for, member.guild.id)) # начать учёт отбытого срока

                        report.set_desc("Забанен на", f"{WARN_TIMEOUT_TIME} дней")
                        await member.timeout(datetime.timedelta(hours=WARN_TIMEOUT_STEP), reason="Превышен лимит предупреждений") 
                        await ctx.send(f"Превышен лимит предупреждений. Чувак <@{member.id}> в муте на {WARN_TIMEOUT_TIME} дней.")

                    connection.commit()
                    connection.close()

                case "ban": 
                    await member.ban(reason = reason)
                    await ctx.send(f"Чувак <@{member.id}> забанен. Причина: {reason}")

                case "mute": 
                    postfix = mute_time[-1] # обозначение единицы времени
                    scalar = int(mute_time[:-1]) # кол-во единиц времени

                    match postfix:
                        case "s":
                            time_delta = datetime.timedelta(seconds=scalar)
                        case "m":
                            time_delta = datetime.timedelta(minutes=scalar)
                        case "h":
                            time_delta = datetime.timedelta(hours=scalar)

                    report.set_desc("Время тайм-аута", mute_time) # изменение сведений репорта
                    await member.timeout(time_delta, reason=reason)
                    await ctx.send(f"Чувак <@{member.id}> в муте на {mute_time}. Причина: {reason}")

                case "unmute":
                    await member.timeout(None)
                    await ctx.send(f"Чувак <@{member.id}> снова с нами.")

                case "unwarn":
                    connection = sqlite3.connect("cogs/warns/warns.db")
                    cursor = connection.cursor()
                    cursor.execute(f"DELETE FROM banned WHERE member_id={member.id}")
                    cursor.execute(f"DELETE FROM users WHERE member_id={member.id}")
                    connection.commit()
                    connection.close()
                    await ctx.send(f"Чувак <@{member.id}> помилован. Все предупреждения сброшены.")

            if one_person_report:
                await report.send(output_channel = output_channel)
            else:
                if not main_report_message.thread:
                    thread = await main_report_message.create_thread(name = main_report_title)
                await report.send(output_channel = thread)


        await ctx.message.delete() # удаление исходной команды
    

    @commands.command() 
    @commands.has_permissions(manage_channels = True)
    async def thisisspecialchannel(self, ctx):
        OUTPUT_CHANNEL_ID = ctx.channel.id
        set_special_channel_id(OUTPUT_CHANNEL_ID)
        await ctx.send(f"Output channel id now is {OUTPUT_CHANNEL_ID}")

        
async def setup(bot):
    await bot.add_cog(IpegaCog(bot))
