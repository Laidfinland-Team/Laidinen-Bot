import discord.ext.commands
from __init__ import *
import discord.ext

import argparse
import subprocess
import time



COGS_FOR_TEST = ['moderationcog', 'delcog', 'example_cog']




print(f"Started at {Style.BRIGHT}cogs test mode")

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
     
     
    await bot.change_presence(status=discord.Status.do_not_disturb, activity=discord.CustomActivity(name="В режиме тестирования🛠"))


@bot.command() 
async def ping(ctx: Ctx):
    await ctx.reply(f'Pong!\n-# **{round(bot.latency * 1000)}ms**')
    output(ctx.channel, f'Pong! {round(bot.latency * 1000)}ms')




"""Cogs loading"""
async def load_cogs():
    for filename in os.listdir("./cogs"):
        if filename.endswith(".py"):
            if filename[:-3] in COGS_FOR_TEST:
                try:
                    await bot.load_extension(f"cogs.{filename[:-3]}")
                except Exception as e:
                    error(f"Failed to load extension {filename}", e)
                    
                    
                    
bot.run(TOKEN)