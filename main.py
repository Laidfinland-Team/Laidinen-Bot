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

        
@bot.command() 
async def ping(ctx):
    await ctx.send(f'Pong! {round(bot.latency * 1000)}ms')
    

#        
#
# Main code end
#       
#

        
"""Cogs loading"""
async def load_cogs():
    for filename in os.listdir("./cogs"):
        if filename.endswith(".py"):
            await bot.load_extension(f"cogs.{filename[:-3]}")

bot.run(TOKEN)
