import sys, os; #sys.path.insert(0, os.path.join(os.getcwd(), ''))

from __init__ import *

from word_game.message import messages
from word_game.main import Game

GAME_STATE = {"author": None, 
              "start": False
              }

class WordGame(commands.Cog):
    """
    A class used to represent a word game cog for a Discord bot.

    ...

    Attributes
    ----------
    bot : discord.ext.commands.Bot
        The Discord bot instance.
    game : Game
        An instance of the Game class.

    Methods
    -------
    on_ready():
        A listener that logs when the bot is ready.
    game_word_start(ctx):
        A command that starts the game and sends a message.
    gw(ctx):
        A command that checks a word according to the game rules.
    setup(bot):
        A setup function to add the WordGame cog to the bot.
    """

    def __init__(self, bot):
        """
        Constructs all the necessary attributes for the WordGame class.

        Parameters
        ----------
        bot : discord.ext.commands.Bot
            The Discord bot instance.
        """
        self.bot = bot
        self.game = Game()

    @commands.Cog.listener() # This is a listener, like @bot.event
    async def on_ready(self):
        """
        Logs when the bot is ready.
        """
        log.info("Word game cog is ready")

    @commands.command() # This is a command, like @bot.command()
    async def game_word_start(self, ctx):
        """
        Starts the game and sends a message.

        Parameters
        ----------
        ctx : discord.ext.commands.Context
            The context of the command.
        """
        GAME_STATE["author"] = ctx.author
        GAME_STATE["start"] = True
        log.info(f"The {GAME_STATE['author']} has started the game.")
        await ctx.send(messages["start-game"])

    @commands.command()
    async def gw(self, ctx):
        """
        Checks a word according to the game rules.

        Parameters
        ----------
        ctx : discord.ext.commands.Context
            The context of the command.
        """
        if GAME_STATE["start"] == True:
            print(await self.game.CheckWord(word))
            match await self.game.CheckWord(word):
                case 0:
                    await ctx.send(messages["missing-word"])
                case 1:
                    log.info(f"Add new word: {word}")
                    await self.game.AddWord(word)
                    await self.game.AddLastSymbol(word[-1])
                    await ctx.send(f"{messages['existing-word']} `{word[-1]}`")
                case 2:
                    await ctx.send(messages["repeated-word"])
                case 3:
                    await ctx.send(f"{messages['wrong-symbol']} `{await self.game.GetLastSymbol()}`")
        else:
            await ctx.send("Игра не началась!")

async def setup(bot):
    """
    A setup function to add the WordGame cog to the bot.

    Parameters
    ----------
    bot : discord.ext.commands.Bot
        The Discord bot instance.
    """
    await bot.add_cog(WordGame(bot))