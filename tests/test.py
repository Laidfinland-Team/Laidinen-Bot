import asyncio
import time




import telebot 
from telebot import *




bot = telebot.TeleBot("TOKEN")

bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.chat.id, "Hello, world!")