from __init__ import *

LOG_DIR = "log.log"


class LogCog(commands.Cog):
    def __init__(self, bot):
        """
        Initialize the LogCog class.

        Parameters:
        bot (discord.ext.commands.Bot): The Discord bot instance.
        """
        self.bot = bot
    
    @commands.Cog.listener()
    async def on_ready(self):
        info("Log cog is ready")

    @commands.has_permissions(administrator=True)
    @commands.command() # This is a command, like @bot.command()
    async def log(self, ctx: Ctx, arg):
        """
        Read and display the last 'arg' lines from the log file.

        Parameters:
        ctx (discord.ext.commands.Context): The context in which the command was invoked.
        arg (str or int): The number of lines to display. If 'all' is provided, all lines will be displayed.

        Returns:
        None
        """
        with open(LOG_DIR, "r", encoding="utf-8") as f:
            lines = f.readlines()

            if arg == 'all' or int(arg) > len(lines):
                arg = len(lines)
            
            pages = TextPaginator.prepare_for_paginate("".join(lines[-int(arg)-1:]), 4000)
            paginator = TextPaginator(ctx, pages[:-1])
            await paginator.paginate()
        
    @commands.has_permissions(administrator=True)
    @commands.command()
    async def info(self, ctx: Ctx, *args):
        text = " ".join(args)   
        info(text)
        await ctx.message.reply("Отправлено в логи ;)")

    @commands.has_permissions(administrator=True)
    @commands.command()
    async def error(self, ctx: Ctx, *args):
        text = " ".join(args)
        error(text)
        await ctx.message.reply("Отправлено в логи ;)")
        
    @commands.has_permissions(administrator=True)
    @commands.command()
    async def warning(self, ctx: Ctx, *args):
        text = " ".join(args)
        warning(text)
        await ctx.message.reply("Отправлено в логи ;)")
        
    @commands.has_permissions(administrator=True)
    @commands.command()
    async def output(self, ctx: Ctx, *args):
        text = " ".join(args)
        output(ctx.channel, text)
        await ctx.message.reply("Отправлено в логи ;)")


        
async def setup(bot):
    """
    Setup function to add the LogCog to the Discord bot.

    Parameters:
    bot (discord.ext.commands.Bot): The Discord bot instance.

    Returns:
    None
    """
    await bot.add_cog(LogCog(bot))