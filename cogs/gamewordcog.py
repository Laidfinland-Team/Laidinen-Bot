import sys, os; #sys.path.insert(0, os.path.join(os.getcwd(), ''))


import requests

from __init__ import *
from database.db_config import host, db_name, user, password, port
from bs4 import BeautifulSoup

URL = "https://gramota.ru/poisk?query={}&mode=all&l=1"

db_params = {
    'host': host,
    'database': db_name ,
    'user': user,
    'password': password
}

table_params = {
    'name': "actual_game"
}


class GameWord(commands.Cog):
    """! Команды для игры в слова"""
    
    def __init__(self, bot):
        self.bot = bot
        
    def check_word_in_page(url, word_to_check):
            response = requests.get(url)
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                div_block = soup.find('div', class_="items common")

            if div_block and word_to_check in div_block.text:
                return True
            
            return False

    @commands.Cog.listener() # This is a listener, like @bot.event
    async def on_ready(self):
        info("GameWord cog is ready")
        
    @commands.command(aliases=["gw"])
    async def gameword(self, ctx, word):
        word = word.lower()
        
        if word in ["last", "lastword", "word"]:
            return await ctx.send(f"**Прошлое слово было: `{db.get_last_word(table_params['name'])}`, тебе на `{db.get_last_word(table_params['name'])[-1]}`!**")
        
        if db.check_word_exists(table_params['name'], word):
            return await ctx.send(f"**Это слово уже нашёл <@{db.get_word_author(table_params['name'], word)}>!**")
        if not db.check_for_table_exist(table_params['name']):
            db.create_actual_game_table()
            return await GameWord.gameword(self, ctx, word)
        
        if not GameWord.check_word_in_page(URL.format(word), word):
            return await ctx.send("**Такого слова не существует!**")
            
    
        if db.get_last_word(table_params['name']):
            i = -1
            ii = -1
            
            while True:
                if db.get_last_word(table_params['name'])[i] in ['ы','ь','ъ']:
                    i -= 1
                else:
                    break
            while True:
                if word[ii] in ['ы','ь','ъ']:
                    ii -= 1
                else:
                    break
            
            if db.get_last_word(table_params['name'])[i] == 'й':
                if word[:1] in ['и','й']:
                    await ctx.send(f"**Отлично, теперь на `{word[ii]}`!**")
                    db.add_word(table_params['name'], ctx.message.author.id, word)
                else:
                    await ctx.send(f"**Это слово начинается на `{word[:1]}`, прошлое слово было: `{db.get_last_word(table_params['name'])}`, тебе на `{db.get_last_word(table_params['name'])[i]}`!**")
            else:
                if word[:1] == db.get_last_word(table_params['name'])[i]:
                    await ctx.send(f"**Отлично, теперь на `{word[ii]}`!**")
                    db.add_word(table_params['name'], ctx.message.author.id, word)
                else:
                    await ctx.send(f"**Это слово начинается на `{word[:1]}`, прошлое слово было: `{db.get_last_word(table_params['name'])}`, тебе на `{db.get_last_word(table_params['name'])[i]}`!**")
        else:
            await ctx.send(f"**Отлично, теперь на `{word[ii]}`!**")
            db.add_word(table_params['name'], ctx.message.author.id, word)
        
            
        
            


        
async def setup(bot):
    await bot.add_cog(GameWord(bot))