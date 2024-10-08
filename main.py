import discord.ext.commands
from __init__ import *
import discord.ext

import argparse
import subprocess
import time

# Создаем парсер для аргументов командной строки
parser = argparse.ArgumentParser(description="Пример программы для работы с аргументами")

# Добавляем аргумент
parser.add_argument('--disabled', type=bool, help='Безопасный режим', required=False)

# Разбираем аргументы
args = parser.parse_args()._get_kwargs()

disabled = args[0][1]

print(f"Started at {Style.BRIGHT + 'normal' if not disabled else 'disabled'} mode")

bot = enabled_bot if not disabled else disabled_bot

if bot == disabled_bot:
    @bot.event
    async def on_connect():
        system("Main bot disabled")

    @bot.event  
    async def on_ready():
        system("Save bot ready")
        
    @bot.command() 
    async def ping(ctx: Ctx):
        await ctx.message.reply(f'Pong!\n-# **{round(bot.latency * 1000)}ms**')
        output(ctx.channel, f'Pong! {round(bot.latency * 1000)}ms')
        
    @bot.command()
    async def start(ctx: commands.Context):
        if ctx.message.author.id != 518516627629801494:
            await ctx.reply("*У тебя нет прав*💔")
            return

        await ctx.reply("Бот включен😎")

        # Закрываем бота
        await bot.close()

        # После закрытия асинхронных задач выполняем синхронный код
        system(Fore.RED + "Main bot started")

        # Используем os.execv для перезапуска процесса
        os.execv(sys.executable, ['python'] + [sys.argv[0]])
        



@bot.event
async def on_connect():
    print(f'{Fore.YELLOW}{Style.BRIGHT}=========================')
    print(f'Connection to discord.com')
    print(f'Token: {hide(TOKEN)}')
    print(f'ID: {bot.user.id}')
    print('Prefix:' + PREFIX )
    print(f'{Fore.YELLOW}{Style.BRIGHT}=========================')
    
    if bot == enabled_bot:
        await load_cogs()
    await bot.change_presence(status = discord.Status.idle, activity = discord.Game(name = "Zzzzzz..."))

@bot.event 
async def on_ready():
    print(f'{Fore.GREEN}{Style.BRIGHT}=========================')
    print(f'Bot logged in as - ')
    print(f'Username: {bot.user.name}')
    print(f'ID: {bot.user.id}')
    print(f'{Fore.GREEN}{Style.BRIGHT}=========================')
    print("Bot connected") 
    print(Style.BRIGHT + "\n\nLogs:\n")
     
    activity = discord.Activity(type=discord.ActivityType.watching, name="видео от Laidfin😎")
    if bot == enabled_bot:
        await bot.change_presence(status=discord.Status.online, activity=activity)
    else:
        await bot.change_presence(status=discord.Status.do_not_disturb, activity=discord.CustomActivity(name="Бот отключен😿"))

@bot.command()
async def status(ctx: Ctx):
    embed = discord.Embed(title="Статус бота", color=discord.Color.green() if bot == enabled_bot else discord.Color.red())
    embed.description=(f"Бот включен😎" if bot == enabled_bot else "Бот отключен😴")
    await ctx.reply(embed=embed)
    info(f"Bot status requested by {ctx.author.name}" + Fore.RED + f" ({"Enabled" if bot == enabled_bot else "Disabled"})")

@bot.command()
async def restart(ctx: Ctx, arg: str = 'None'):
    if ctx.message.author.id != 518516627629801494:
        await ctx.reply("У тебя нет прав💔")
        return
    if arg.lower() not in ['s', 'd']:
        # Закрываем соединение и останавливаем бота
        try:
            await ctx.reply("Бот перезапущен♻")
        except:
            pass
    else:
        await ctx.message.add_reaction("✅")
        await asyncio.sleep(1)
        await ctx.message.delete()
    
    await bot.close()
    system(Fore.RED + "Bot restarted")

    # Опционально: если хотите перезапустить бота без участия внешнего процесса, используйте это
    for t in asyncio.all_tasks():
        t.cancel()
    
    os.execv(sys.executable, ['python'] + sys.argv + [f'{'--disabled DISABLED' if disabled else ""}'])
    
@bot.command()
async def kill_bot(ctx: Ctx):
    if ctx.author.id != 518516627629801494: # Декоратор не использован в целях надёжности.
        await ctx.reply("*У тебя нет прав*💔")
        return
    try:
        await ctx.reply("Бот ***УБИТ***🥵")
    except:
        pass
    try:
        
        tasks = asyncio.all_tasks()
        active_tasks = [task for task in tasks if not task.done()]  # Фильтруем незавершенные задач
        
        await asyncio.wait_for(bot.close(), timeout=5)
        
        system(Fore.RED + "Bot killed")
        
    except Exception as e:
        error("Failed to kill bot", e)
        await ctx.reply("Не удалось убить бота⚠")
    
    exit()
    exit()

if bot == enabled_bot:

    @bot.command() 
    async def ping(ctx: Ctx):
        await ctx.reply(f'Pong!\n-# **{round(bot.latency * 1000)}ms**')
        output(ctx.channel, f'Pong! {round(bot.latency * 1000)}ms')
        
    @bot.command()
    async def stop(ctx: Ctx):
        if ctx.message.author.id != 518516627629801494:
            await ctx.reply("*У тебя нет прав*💔")
            return
        
        await ctx.reply("Бот отключен😴")
        await asyncio.wait_for(bot.close(), timeout=5)
        system(Fore.RED + "Bot stopped")
        
        os.execv(sys.executable, ['python'] + sys.argv + ['--disabled DISABLED'])
        exit()
        
class TextCog(commands.Cog):
    color_dict = {
            "red": 0xFF0000,
            "green": 0x00FF00,
            "blue": 0x0000FF,
            "yellow": 0xFFFF00,
            "purple": 0x800080,
            "orange": 0xFFA500,
            "black": 0x000000,
            "white": 0xFFFFFF
        }
    
    def __init__(self, bot):
        self.bot = bot
        
    @commands.Cog.listener()
    async def on_ready(self):
        info("Text cog is ready")
        
    @commands.command()
    @is_hellcat()
    async def t(self, ctx: Ctx, *text):
        await bot.get_command('text').callback(self, ctx, text)

    @commands.command()
    @is_hellcat()
    async def text(self, ctx: Ctx, *text):
        text = " ".join(*text)
        await ctx.message.delete()
        if ctx.message.reference:
            message = await ctx.fetch_message(ctx.message.reference.message_id)
            await message.reply(text)
        else:
            await ctx.send(text)
        output(ctx.channel, text)
        

    @commands.command()
    @is_hellcat()
    async def f(self, ctx: Ctx, count: str, *text):
        await bot.get_command('flood').callback(self, ctx, count, text)
        
    @commands.command()
    @is_hellcat()
    async def flood(self, ctx: Ctx, count: str, *text):
        count = int(count)
        text = " ".join(*list(text))
        if text == "":
            await ctx.reply("Не умею отправлять пустые сообщения")
            return
        
        await ctx.message.delete()
        
        for i in range(count):
            if ctx.message.reference:
                message = await ctx.fetch_message(ctx.message.reference.message_id)
                await message.reply(text)
            else:
                await ctx.send(text)
        output(ctx.channel, f"Message {text} sent {count} times")
        
    @commands.command()
    @is_hellcat()
    async def pf(self, ctx: Ctx, count: str, *text):
        await bot.get_command('ping_flood').callback(self, ctx, count, text)
        
    @commands.command()
    @is_hellcat()
    async def ping_flood(self, ctx: Ctx, count: str, *text):
        count = int(count)
        
        text = " ".join(*list(text))
        if text == "":
            await ctx.reply("Не умею отправлять пустые сообщения")
            return
        
        await ctx.message.delete()
        
        for i in range(count):
            if ctx.message.reference:
                message = await ctx.fetch_message(ctx.message.reference.message_id)
                flood = await message.reply(text)
            else:
                flood = await ctx.send(text)
            await flood.delete()
        output(ctx.channel, f"Message {text} sent {count} times")
                

    @commands.command()
    @is_hellcat()
    async def c(self, ctx: Ctx, *text):
        await bot.get_command('change').callback(self, ctx, text)

    @commands.command()
    @is_hellcat()
    async def change(self, ctx: Ctx, *text):
        text  = " ".join(*text)
            
            
        message: discord.Message = await ctx.fetch_message(ctx.message.reference.message_id)
        
        if not message.embeds and not text:
            await ctx.reply("Не могу создать пустое сообщение")
            return
        
        message = await message.edit(content=text)
        
        
        if message:
            output(ctx.channel, f"Message with id {message.id} successful edited")
            await ctx.reply(f"Сообщение успешно изменено!")
            
            
    @commands.command()
    @is_hellcat()
    async def e(self, ctx: Ctx, title, text, reactions=None, color=MAIN_COLOR):
        await bot.get_command('send_embed').callback(self, ctx, title, text, reactions=reactions, color=color) 
        
    @commands.command()
    @is_hellcat()
    async def send_embed(self, ctx: Ctx, title, text, reactions=None, color=MAIN_COLOR):
        if not color == MAIN_COLOR:
            color = TextCog.color_dict.get(color.lower(), 0x000000)  # Default to black if color not found
        embed = discord.Embed(title=title, description=text, color=color)
        message = await ctx.send(embed=embed)
        if reactions:
            for reaction in reactions.split(" "):
                ic(reaction)
                await message.add_reaction(reaction)
        await atrys(ctx.message.delete)
        output(ctx.channel, f"Embed message sent with title {title} and color {color}")
            
    @commands.command()
    @is_hellcat()
    async def ce(self, ctx: Ctx, title=None, text=None, color=MAIN_COLOR):
        await bot.get_command('change_embed').callback(self, ctx, title, text)
        
    @commands.command()
    @is_hellcat()
    async def change_embed(self, ctx: Ctx, title=None, text=None, color=None):
        if title == "None":
            title = None
        if text == "None":
            text = None
        if not color == None:
            color = TextCog.color_dict.get(color.lower(), 0x000000)
            
        if color == 'main':
            color = MAIN_COLOR
            
        if not title and not text:
            await ctx.reply("Не могу создать пустое сообщение")
            return
        
        message: discord.Message = await ctx.fetch_message(ctx.message.reference.message_id)
        
        if color == None:
            color = message.embeds[0].color
        
        if not message.embeds and not text:
            await ctx.reply("Не могу создать пустое сообщение")
            return
        if not title:
            title = message.embeds[0].title
        if not text:
            text = message.embeds[0].description
        
        embed = discord.Embed(title=title, description=text, color=color)
        await message.edit(embed=embed)
        output(ctx.channel, f"Embed message with id {message.id} successful edited")
        await ctx.reply(f"Сообщение успешно изменено!")
            
    @commands.command()
    @is_hellcat()
    async def r(self, ctx: Ctx, reaction: str):
        await bot.get_command('reaction').callback(self, ctx, reaction)
        
    @commands.command()
    @is_hellcat()
    async def reaction(self, ctx: Ctx, reaction: str):
        message: discord.Message = await ctx.fetch_message(ctx.message.reference.message_id)
        await ctx.message.delete()
        await message.add_reaction(reaction)
        output(ctx.channel, f"Reaction {reaction} added to message with id {message.id}")
        
            
    @commands.command()
    @is_hellcat()
    async def d(self, ctx: Ctx):
        await bot.get_command('delete').callback(self, ctx)
        
    @commands.command()
    @is_hellcat()
    async def delete(self, ctx: Ctx):
        
        message: discord.Message = await ctx.fetch_message(ctx.message.reference.message_id)
        await message.delete()
        output(ctx.channel, f"Message with id {message.id} successful deleted")
        if type(ctx.channel) != discord.DMChannel:
            await ctx.reply("Сообщение успешно удалено!")
        
        


    

#        
#
# Main code end
#       
#


"""Cogs loading"""
async def load_cogs():
    for filename in os.listdir("./cogs"):
        if filename.endswith(".py"):
            try:
                await bot.load_extension(f"cogs.{filename[:-3]}")
            except Exception as e:
                error(f"Failed to load extension {filename}", e)
    await bot.add_cog(TextCog(bot))

bot.run(TOKEN)