import discord
from discord.ext import commands


bot = commands.Bot(command_prefix='?', help_command=None, intents=discord.Intents.all())

@bot.event
async def on_ready():
    print(f'We have logged in as {bot.user}')

@bot.command()
async def test(ctx, arg):
    await ctx.send(arg)
    

bot.run('MTE4NDU5NjA0NDUwODU2NTY1NA.GIkofI.PCTaz67cBgl1-vMa5lrxjx8FvhPYcFlszL7wic')