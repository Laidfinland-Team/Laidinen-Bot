import sys, os

import discord.types; #sys.path.insert(0, os.path.join(os.getcwd(), ''))
import socket

from __init__ import *
from ds_poker.ds_poker import Game, Player
from ds_poker.cards_connector import Board, Hand
import threading



asyncio_sleep_time = 1

class Game_self:
            def __init__(self):
                self.global_players: list[Player] = []
                self.game: Game = None
                
class PokerCog(commands.Cog):

                
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener() # This is a listener, like @bot.event
    async def on_ready(self):
        info("Poker cog is ready")
        
    @commands.command() # This is a command, like @bot.command()
    async def start_poker(self, ctx):
        game_self = Game_self() 
        banner = discord.File(r"ds_poker\images\banner.png")
        await ctx.send("poker", embed=Unjoined_view(game_self).embed, file=banner, view=Unjoined_view(game_self))

    async def check_for_interaction(interaction : discord.Interaction):
        return True
        """ channel = bot.get_channel(interaction.channel.id)
        message = await channel.fetch_message(interaction.message.id)
        if message != None:
            return ic(True)
        else:
            return ic(False) """

    def send_message_to_server(message, server_address='localhost', port=8000):
        # Create a TCP/IP socket
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        
        try:
            # Connect the socket to the server
            sock.connect((server_address, port))
            
            # Send the message
            sock.sendall(message.encode('utf-8'))
            
            # Optional: Receive response from the server (if any)
            response = sock.recv(1024)
            print('Received:', response.decode('utf-8'))
            
        except ConnectionRefusedError:
            print("Connection refused. Ensure the server is running and accessible.")
            
        finally:
            # Close the socket
            print("456")
            sock.close()


    async def start_game(game_self: Game_self):
        board = discord.File(rf"ds_poker\images\boards\{Board(game_self.game.table.board)()}.png")
        await game_self.global_players[0].interaction.followup.send(file=board, embed=Round_view(game_self).embed, view=Round_view(game_self))
        for player in game_self.global_players:
            await player.message.delete()
            
            
            if len(game_self.game.players) == 2:
                game_self.game.players[0].my_turn = True
            else:
                game_self.game.players[2].my_turn = True
            game_self.game.bet(game_self.game.players[0], game_self.game.small_blind)
            game_self.game.bet(game_self.game.players[1], game_self.game.big_blind)
            hand = discord.File(rf"ds_poker\images\hands\{Hand(player.hand)()}.png")
            player.message = await player.interaction.followup.send(file=hand, ephemeral=True, view=Hand_view(game_self, player), embed=Hand_view(game_self, player).embed)
            await game_self.game.next_round()
            
    async def next_player(game_self : Game_self):
        if game_self.game.round_over:
            await game_self.game.next_round()
            game_self.game.round_over = False
        for player in game_self.game.players:
            await player.message.delete()
            hand = discord.File(rf"ds_poker\images\hands\{Hand(player.hand)()}.png")
            player.message = await player.interaction.followup.send(file=hand, ephemeral=True, view=Hand_view(game_self, player), embed=Hand_view(game_self, player).embed)
        
        #await game.next_round()
    async def refresh_views(game_self : Game_self, round : int, interaction : discord.Interaction, code : str):
        if code in ["join", "exit"]:
            for player in game_self.global_players:
                host = True if player == game_self.global_players[0] else False
                if str(player) == str(interaction.user.id):
                    player.interaction = interaction
                    ic(type(Joined_view(game_self, host)))
                    player.message = await interaction.followup.send(ephemeral=True, content="123", view=Joined_view(game_self, host), embed=Joined_view(game_self, host).embed)
                else:
                    await player.message.delete()
                    player.message = await player.interaction.followup.send(ephemeral=True, view=Joined_view(game_self, host), embed=Joined_view(game_self, host).embed)
        if code == "start":
            await PokerCog.start_game(game_self)
        
class Buttons(PokerCog):
    class Join_button(discord.ui.Button):
        def __init__(self, game_self : Game_self):
            self.game_self = game_self
            super().__init__(label="Join", style=discord.ButtonStyle.green)
            
        async def callback(self, interaction: discord.Interaction):
            if str(interaction.user.id) in [str(player) for player in self.game_self.global_players]:
                return
            player = Player(str(interaction.user.id))
            self.game_self.global_players.append(player)
            try:
                await interaction.response.defer()
            except:
                pass
            while not await PokerCog.check_for_interaction(interaction):
                pass
            await asyncio.sleep(asyncio_sleep_time)
            await PokerCog.refresh_views(self.game_self, -1, interaction, code="join")
                    
            
    class Exit_button(discord.ui.Button):
        def __init__(self, game_self: Game_self):
            super().__init__(label="Exit", style=discord.ButtonStyle.red)
            self.game_self = game_self
            
        async def callback(self, interaction: discord.Interaction):
            for player in self.game_self.global_players:
                if str(player) == str(interaction.user.id):
                    await player.message.delete()
                    self.game_self.global_players.remove(player)
            try:
                await interaction.response.defer()
            except:
                pass
            
            await asyncio.sleep(asyncio_sleep_time)
            await PokerCog.refresh_views(self.game_self, -1, interaction, code="exit")
            await PokerCog.next_player(self.game_self)
            
    class Start_button(discord.ui.Button):
        def __init__(self, game_self: Game_self, disable=False):
            super().__init__(label="Start", style=discord.ButtonStyle.green, disabled=disable)
            self.game_self = game_self
            
        async def callback(self, interaction: discord.Interaction):
            game = Game(self.game_self.global_players, 2)
            self.game_self.game = game
            self.game_self.game.new_game()
            self.game_self.global_players = game.players
            try:
                await interaction.response.defer()
            except:
                pass
            #while not await check_for_interaction(interaction):
                #pass
            await asyncio.sleep(asyncio_sleep_time)
            await PokerCog.refresh_views(self.game_self, 0, interaction, code="start")
            await PokerCog.next_player(self.game_self)

    class Check_button(discord.ui.Button):
        def __init__(self, game_self: Game_self):
            self.game_self = game_self
            super().__init__(label="Check", style=discord.ButtonStyle.grey)
            
        async def callback(self, interaction: discord.Interaction):
            try:
                await interaction.response.defer()
            except:
                pass
            #while not await check_for_interaction(interaction):
            # pass
            
            PokerCog.send_message_to_server("check")
            
            await PokerCog.next_player(self.game_self)
            
    class Call_button(discord.ui.Button):
        def __init__(self, game_self : Game_self):
            self.game_self = game_self
            super().__init__(label="Call", style=discord.ButtonStyle.green)
            
        async def callback(self, interaction: discord.Interaction):
            try:
                await interaction.response.defer()
            except:
                pass
            while not await PokerCog.check_for_interaction(interaction):
                pass
            
            PokerCog.send_message_to_server("call")
                    
            await PokerCog.next_player(self.game_self)
            
    class Bet_button(discord.ui.Button):
        def __init__(self, game_self: Game_self, label):
            self.label_text = label
            self.game_self = game_self
            super().__init__(label=label, style=discord.ButtonStyle.green)
            
        async def callback(self, interaction: discord.Interaction):
            try:
                await interaction.response.defer()
            except:
                pass
            while not await PokerCog.check_for_interaction(interaction):
                pass
            for player in self.game_self.game.players:
                if str(player) == interaction.user.id:
                    player.action = self.label_text
            await interaction.response.defer()
            await PokerCog.next_player(self.game_self)
    class Fold_button(discord.ui.Button):
        def __init__(self, game_self : Game_self):
            self.game_self = game_self
            super().__init__(label="Fold", style=discord.ButtonStyle.red)
            
        async def callback(self, interaction: discord.Interaction):
            for player in self.game_self.game.players:
                if str(player) == interaction.user.id:
                    player.action = "fold"
            await interaction.response.defer()
        
        
        


class Unjoined_view(discord.ui.View):
        
    def __init__(self, game_self: Game_self):
        super().__init__()
        self.add_item(Buttons.Join_button(game_self))
        self.embed = discord.Embed()
        self.embed.set_image(url="attachment://banner.png")
        
        
class Joined_view(discord.ui.View):
    def __init__(self, game_self: Game_self, host=False):
        super().__init__()
        self.add_item(Buttons.Exit_button(game_self))
        if host:
            disable = True if len(game_self.global_players) == 1 else False
            self.add_item(Buttons.Start_button(game_self, disable))
            
        match len(game_self.global_players):
            case 0:
                color = discord.Color.red()
            case 1:
                color = discord.Color.red()
            case 2:
                color = discord.Color.orange()
            case 3:
                color = discord.Color.orange()
            case _:
                color = discord.Color.green()
                
        self.embed = discord.Embed(description=f"**Host:** <@{game_self.global_players[0]}>\n\n**Players:** {', '.join([f"<@{str(player)}>" for player in game_self.global_players])}\n\n**{len(game_self.global_players)}/9**", color=color)
        
class Round_view(discord.ui.View):
    def __init__(self, game_self: Game_self):
        super().__init__()
        self.game = game_self.game
        self.embed = discord.Embed()
        self.add_item(Buttons.Exit_button(game_self))
        board_id = Board(game_self.game.table.board)()
        self.embed.set_image(url=f"attachment://{board_id}.png")

class Hand_view(discord.ui.View):
    def __init__(self, game_self: Game_self, player: Player):
        super().__init__()
        self.player = player
        self.embed = discord.Embed()
        self.game = game_self.game
        if self.player.my_turn:
            if self.game.table.last_bet == 0:
                self.add_item(Buttons.Check_button(game_self))
            else:
                self.embed = discord.Embed(title=f"Amount to call: {game_self.game.table.last_bet - self.player.round_chips}", color=discord.Color.green())
                self.add_item(Buttons.Call_button(game_self))
            if self.game.table.last_raiser == None:
                self.add_item(Buttons.Bet_button(game_self, "Bet"))
            else:
                self.add_item(Buttons.Bet_button(game_self, "Raise"))
            self.add_item(Buttons.Fold_button(game_self))
        hand_id = Hand(player.hand)()
        self.embed.set_image(url=f"attachment://{hand_id}.png")
        
        
async def setup(bot: commands.Bot):
    await bot.add_cog(PokerCog(bot))