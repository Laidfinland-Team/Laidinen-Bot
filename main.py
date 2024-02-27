from __init__ import *


@bot.event
async def on_connect():
    print(f'{Fore.YELLOW}{Style.BRIGHT}=========================')
    print(f'Connection to discord.com')
    print(f'Token: {hide(TOKEN)}')
    print(f'ID: {bot.user.id}')
    print('Prefix:' + PREFIX )
    print(f'{Fore.YELLOW}{Style.BRIGHT}=========================')

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
     
    activity = discord.Activity(type=discord.ActivityType.watching, name="видео от Laidfin")
    await bot.change_presence(status=discord.Status.online, activity=activity)

        
@bot.command(brief = "Проверка задержки с ботом") 
async def ping(ctx):
    await ctx.send(f'Pong! {round(bot.latency * 1000)}ms')
    
@bot.command(brief = "Пригласить участвовать в разработке бота")
async def invite(ctx, member : discord.Member = None):
    await ctx.send(f"<@{member.id}>")
    await ctx.send(embed=discord.Embed(description="**Привет путник, я вижу ты шаришь за прогерские штучки, не хочешь принять участие в разработке серверного бота?**\n\nЕсли да, тебе сюда: <#1201633718985572352>!", color=discord.Color.green()))

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
                error(f"Failed to load extension {filename}: {e}")

bot.run(TOKEN)