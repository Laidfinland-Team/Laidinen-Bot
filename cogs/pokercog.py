import sys, os; #sys.path.insert(0, os.path.join(os.getcwd(), ''))

from __init__ import *
from ds_poker.ds_poker import Game, Player
from ds_poker.cards_connector import Board


global_players : list[Player] = []

game : Game = None

def start_game():
    for player in global_players:
        player.interaction.delete_original_response()
        player.interaction.channel.send(embed=Round_view(game).embed, view=Round_view(game))

class Buttons():
    class Join_button(discord.ui.Button):
        def __init__(self):
            super().__init__(label="Join", style=discord.ButtonStyle.green)
            
        async def callback(self, interaction: discord.Interaction):
            player = Player(str(interaction.user.id))
            global_players.append(player)
            file = discord.File(r"C:\Users\Alena\Desktop\Laidfinland\Laidinen-Bot\concatenated_image.png")
            if global_players[0] == player:
                host = True
            else:
                host = False
            await interaction.response.send_message(ephemeral=True, embed=Joined_view().embed, file=file, view=Joined_view(host))
            player.interaction = interaction
                    
            
    class Exit_button(discord.ui.Button):
        def __init__(self):
            super().__init__(label="Exit", style=discord.ButtonStyle.red)
            
        async def callback(self, interaction: discord.Interaction):
            banner = discord.File(r"ds_poker\images\banner.png")
            for player in global_players:
                if str(player) == str(interaction.user.id):
                    global_players.remove(player)
            await interaction.response.defer()
            await interaction.delete_original_response(
            )
            
    class Start_button(discord.ui.Button):
        def __init__(self):
            super().__init__(label="Start", style=discord.ButtonStyle.green)
            
        async def callback(self, interaction: discord.Interaction):
            game = Game(global_players, 100)
            game.new_game()
            board = discord.File(rf"ds_poker\images\boards\{Board(game.table.board)()}.png") 
            await interaction.response.defer()
            await interaction.delete_original_response()
            await interaction.channel.send(file=board, embed=Round_view(game).embed, view=Round_view(game))
            
    class Check_button(discord.ui.Button):
        def __init__(self):
            super().__init__(label="Check", style=discord.ButtonStyle.green)
            
        async def callback(self, interaction: discord.Interaction):
            await interaction.message.edit(view=Round_view()) 
            await interaction.response.defer()
            
    class Call_button(discord.ui.Button):
        def __init__(self):
            super().__init__(label="Call", style=discord.ButtonStyle.grey)
            
        async def callback(self, interaction: discord.Interaction):
            await interaction.message.edit(view=Round_view()) 
            await interaction.response.defer()
            
    class Raise_button(discord.ui.Button):
        def __init__(self, bet_or_raise):
            if bet_or_raise == "bet":
                label = "Bet"
            elif bet_or_raise == "raise":
                label = "Raise"
            super().__init__(label=label, style=discord.ButtonStyle.red)
            
        async def callback(self, interaction: discord.Interaction):
            await interaction.message.edit(view=Round_view()) 
            await interaction.response.defer()
            
    class Fold_button(discord.ui.Button):
        def __init__(self):
            super().__init__(label="Fold", style=discord.ButtonStyle.red)
            
        async def callback(self, interaction: discord.Interaction):
            await interaction.message.edit(view=Round_view()) 
            await interaction.response.defer()
        
        
        


class Unjoined_view(discord.ui.View):
        
    def __init__(self):
        super().__init__()
        self.add_item(Buttons.Join_button())
        self.embed = discord.Embed()
        self.embed.set_image(url="attachment://banner.png")
        
        
class Joined_view(discord.ui.View):
    def __init__(self, host=False):
        super().__init__()
        self.add_item(Buttons.Exit_button())
        if host:
            self.add_item(Buttons.Start_button())
        self.embed = discord.Embed(description=f"**Host:** <@{global_players[0]}>\n\n**Players:** {', '.join([f"<@{str(player)}>" for player in global_players])}\n\n**{len(global_players)}/9**", color=discord.Color.green())
        
class Round_view(discord.ui.View):
    def __init__(self, game : Game):
        super().__init__()
        self.game = game
        self.embed = discord.Embed()
        board_id = Board(game.table.board)()
        self.embed.set_image(url=f"attachment://{board_id}.png")
        bet_or_raise = "bet" if game.table.last_raiser == None else "raise"
        self.add_item(Buttons.Check_button())
        self.add_item(Buttons.Fold_button())
        self.add_item(Buttons.Raise_button(bet_or_raise))
        self.add_item(Buttons.Call_button())
        
        
class PokerCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener() # This is a listener, like @bot.event
    async def on_ready(self):
        info("Poker cog is ready")
        
    @commands.command() # This is a command, like @bot.command()
    async def start_poker(self, ctx):
        # Send embed with image
        banner = discord.File(r"ds_poker\images\banner.png")
        for i in global_players:
            print(i)
        await ctx.send("hello", embed=Unjoined_view().embed, file=banner, view=Unjoined_view())
        
async def setup(bot):
    await bot.add_cog(PokerCog(bot))