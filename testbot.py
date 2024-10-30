import discord.ext.commands
from __init__ import *
import discord.ext

import argparse
import subprocess
import time


print(f"Started at {Style.BRIGHT}test mode")

@bot.event
async def on_connect():
    print(f'{Fore.YELLOW}{Style.BRIGHT}=========================')
    print(f'Connection to discord.com')
    print(f'Token: {hide(TOKEN)}')
    print(f'ID: {bot.user.id}')
    print('Prefix:' + PREFIX )
    print(f'{Fore.YELLOW}{Style.BRIGHT}=========================')
    
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
     
     
    await bot.change_presence(status=discord.Status.do_not_disturb, activity=discord.CustomActivity(name="В режиме тестирования🛠"))


@bot.command() 
async def ping(ctx: Ctx):
    await ctx.reply(f'Pong!\n-# **{round(bot.latency * 1000)}ms**')
    output(ctx.channel, f'Pong! {round(bot.latency * 1000)}ms')


async def main():
    thread = await bot.fetch_channel(1293981880789766278)
    

    
                    
                    
bot.run(TOKEN)