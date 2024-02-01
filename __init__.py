import discord
import colorama 
import asyncio
import importlib.util
import os
import sys

#from TOKEN import TOKEN # Раскомментируйте эту строку если вы используете TOKEN.py внутри рабочей директории
from bot_params import PREFIX
from _con_message_base import *
from _functions_base import *

from discord.ext import commands
from pretty_help import PrettyHelp
from accessify import protected, private
from colorama import Fore, Style, Back
from icecream import ic


__AUTH_FILE_PATH = os.path.dirname(os.getcwd()) + '\TOKEN.py'

MAIN_COLOR = discord.Color.purple()

colorama.init(autoreset=True)
intents = discord.Intents.default()



bot = commands.Bot(command_prefix=PREFIX, help_command=PrettyHelp(color=MAIN_COLOR, no_category="Technical Commands"), intents=discord.Intents.all())


__spec = importlib.util.spec_from_file_location('AUTH', __AUTH_FILE_PATH)
__auth = importlib.util.module_from_spec(__spec)
__spec.loader.exec_module(__auth)
TOKEN = __auth.TOKEN

ic(discord.__version__)