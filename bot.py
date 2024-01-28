import discord
from discord.ext import commands
from colorama import Fore, Style

intents = discord.Intents.default()
intents.message_content = True
intents.guilds = True
#intents.channels = True
prefix = '?'

bot = commands.Bot(command_prefix='!', intents=intents)
TOKEN = "MTE4NDU5NjA0NDUwODU2NTY1NA.GIkofI.PCTaz67cBgl1-vMa5lrxjx8FvhPYcFlszL7wic"

@bot.event
async def on_connect():
	print(f'{Fore.YELLOW}{Style.BRIGHT}=========================')
	print(f'Connection to discord.com')
	print(f'Token: {TOKEN}')
	print(f'ID: {bot.user.id}')
	print('Prefix:' + prefix )
	print(f'{Fore.YELLOW}{Style.BRIGHT}=========================')

	await bot.change_presence(status = discord.Status.idle, activity = discord.Game(name = "Zzzzzz..."))

@bot.event # Создаём событие.
async def on_ready(): # Задаём условие готовности.
    print(f'{Fore.GREEN}{Style.BRIGHT}=========================')
    print(f'Bot logged in as - ')
    print(f'Username: {bot.user.name}')
    print(f'ID: {bot.user.id}')
    print(f'{Fore.GREEN}{Style.BRIGHT}=========================')
    print("Bot connected")  

    activity = discord.Game(name="Игры | $help", type=3)
    await bot.change_presence(status=discord.Status.online, activity=activity)
    while 1:
        text = input()
        await send_msg(1156941990672466020, text)

async def send_msg(channel_id, text):
    channel = bot.get_channel(channel_id) #  Gets channel from internal cache
    await channel.send(text) #  Sends message to channel

@bot.event
async def on_guild_channel_delete(channel):
    # Здесь вы можете обработать удаление канала
    user_id = None

    async for entry in channel.guild.audit_logs(action=discord.AuditLogAction.channel_delete, limit=1):
        if entry.target.id == channel.id:
            user_id = entry.user.id
            break

    if user_id:
        user = bot.get_user(user_id)
        print(f'Канал {channel.name} удален пользователем {user_id}')

bot.run(TOKEN)