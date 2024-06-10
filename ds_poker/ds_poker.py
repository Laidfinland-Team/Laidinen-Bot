import poker
import PokerPy
import random
import discord
import time
import asyncio
import socket
import threading

from icecream import ic

answer = None
def start_server(host='localhost', port=8000):
    global answer
    # Create a TCP/IP socket
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    
    # Bind the socket to the address and port
    server_socket.bind((host, port))
    
    # Listen for incoming connections
    server_socket.listen(1)
    print(f"Server started and listening on {host}:{port}")
    
    while True:
        # Wait for a connection
        print("Waiting for a connection...")
        connection, client_address = server_socket.accept()
        
        try:
            print(f"Connection from {client_address}")
            
            # Receive the data in small chunks and print it
            while True:
                data = connection.recv(1024)
                if data:
                    answer = data.decode('utf-8')
                    print(f"Received: {data.decode('utf-8')}")
                    # Send a response back to the client (optional)
                    connection.sendall(b"Message received")
                    # Clean up the connection
                    connection.close()
                    connection = None
                    # Stop the server and release the address
                    server_socket.close()
                    return
                else:
                    break
        finally:
            # Clean up the connection
            if connection != None:
                connection.close()

def poker_input(prompt, answers, table):
    while True:
        answer = input(prompt)
        try:
            if answer.split()[0] in answers:
                if answer.split()[0] == "raise":
                    if float(answer.split()[1]) < table.big_blind:
                        print("Invalid raise")
                        continue
                return answer
            else:
                print("Invalid input")
        except:
            print("Invalid input")
            
class Combo():
    """!
    Класс который реализовывает комбинации карт.
    @details Сначала получает 7 карт, последующие методы реализовывают эти карты.
    @param [in] cards список из 7 карт (5 на столе и 2 в руке)
    
    """
    def __init__(self, cards):
        self.cards = cards

    def get_combo(self):
        """! Возвращает лучшую комбинацию из 5 карт (3 на столе и 2 в руке)
        @return <PokerPy.Hand> - list[PokerPy.Card] - список из 5 карт
        """
        return PokerPy.get_best_hand(self.cards)
    
    def hand_heuristic(self):
        """! Возвращает числовое представление силы комбинации
        @details Используется для сравнения комбинаций и выявления победителя
        @return <int> - числовое представление силы комбинации
        """
        return PokerPy.get_best_hand(self.cards).hand_heuristic()

class Player:
    def __init__(self, name):
        self.name = name
        self.hand = []
        self.combo : PokerPy.Hand
        self.combo_heuristic : int
        self.fold = False
            
        self.stack = 0
        self.nested_chips = 0
        self.round_chips = 0
        
        """Discord"""
        self.interaction : discord.Interaction = None
        self.message : discord.InteractionMessage = None
        self.my_turn : bool = False
        self.action : str = None
    
    def __repr__(self):
        return self.name
    
    async def wait_for_action(self, game):
        global answer
        threading.Thread(target=start_server).start()
        
        self.my_turn = True
        while answer == None:
            await asyncio.sleep(0.5)
            
        self.my_turn = False
            
        self.action = answer
        answer = None
        
        match self.action.split()[0]:
            case "fold":
                self.fold = True
                return "fold"
            case "check":
                return "check"
            case "call":
                return "call", float(game.table.last_bet - self.round_chips)
            case "raise":
                return "raise", float(self.action.split()[1])
            case _:
                print("Invalid action")
                return self.wait_for_action()
    def bet(self, amount):
        self.stack -= amount
        self.nested_chips += amount
        self.round_chips += amount

class Table:
    def __init__(self, deck):
        self.bank = 0
        self.last_bet = 0
        self.last_raiser : Player = None
        
        self.flop = deck.pop(), deck.pop(), deck.pop()
        self.turn = deck.pop()
        self.river = deck.pop()
        self.board = []
        
        

class Game:

    def __init__(self, players: list[Player], big_blind):
        self.small_blind = big_blind / 2
        self.big_blind = big_blind
        self.players = players
        self.rating: list[int]
        self.winners: list[Player]
        
        deck = list(poker.Card)
        for i, card in enumerate(deck):
            card = str(card)
            deck[i] = PokerPy.Card(card.replace("♠", "S").replace("♥", "H").replace("♣", "C").replace("♦", "D").replace("T", "10"))
        random.shuffle(deck)
        self.deck = deck
        
        self.round = 0
class Game:
    def __init__(self, players, big_blind):
        self.small_blind = big_blind / 2
        self.big_blind = big_blind
        self.players = players
        self.round_over: bool = False
        self.rating : list[int]
        self.winners : list[Player]
        
        deck = list(poker.Card)
        for i, card in enumerate(deck):
            card = str(card)
            deck[i] = PokerPy.Card(card.replace("♠", "S").replace("♥", "H").replace("♣", "C").replace("♦", "D").replace("T", "10"))
        random.shuffle(deck)
        self.deck = deck
        
        self.round = 0
        
    def bet(self, player, amount):
        player.bet(amount)
        self.table.bank += amount
        self.table.last_bet = player.round_chips
    
    def new_game(self):
        for player in self.players:
            player.hand = self.deck.pop(), self.deck.pop()
        self.table = Table(self.deck)
        
    def is_one_players_left(self):
        return len([player for player in self.players if player.fold]) == len(self.players) - 1
    
    async def round_cycle(self):
        first_cycle = True
        
        while not all(player.round_chips == self.table.last_bet for player in self.players if not player.fold) or first_cycle:
            for i, player in enumerate(self.players):
                # print(i, player)
                if player == self.table.last_raiser:
                    break
                if self.is_one_players_left():
                    break
                
                if player.fold:
                    continue
                if self.round == 0 and first_cycle:
                    if i == 0:
                        #self.bet(player, self.small_blind) 
                        continue
                    elif i == 1:
                        #self.bet(player, self.big_blind)
                        continue
                elif self.round == 0 and not first_cycle:
                    if i > 1:
                        break
                    
                print(f"Player {player} turn")
                action = await player.wait_for_action(self)
                    
                match action[0]:
                    case "fold":
                        continue
                    case "check":
                        continue
                    case "call":
                        self.bet(player, action[1])
                    case "raise":
                        self.bet(player, action[1])
                        self.table.last_raiser = player
            first_cycle = False
        print("Round end")
        self.round_over = True
        
    async def next_round(self):
        if self.round != 0:
            for player in self.players:
                player.round_chips = 0
            self.table.last_bet = 0
            self.table.last_raiser = None
        match self.round:
            case 0:
                pass
            case 1:
                for card in self.table.flop:
                    self.table.board.append(card)
            case 2:
                self.table.board.append(self.table.turn)
            case 3:
                self.table.board.append(self.table.river)
            case _:
                return self.determinate_winner()
                
        await self.round_cycle()
        self.round += 1
        
    def determinate_winner(self):
        if self.is_one_players_left():
            for player in self.players:
                if not player.fold:
                    print(f"{player} wins")
                    player.stack += self.table.bank
                    self.table.bank = 0
                    return
        else:
            for player in self.players:
                if player.fold:
                    continue
                player_combo = Combo(list(player.hand) + self.table.board).get_combo()
                player.combo = player_combo
                player.combo_heuristic = player_combo.hand_heuristic()
            winners = [player.combo_heuristic for player in self.players if not player.fold]
            winner = max(winners)
            rating = winners.sort()
            winners = []
            for player in self.players:
                if player.combo_heuristic == winner and not player.fold:
                    winners.append(player)
            self.rating = rating
            self.winners = winners
            self.end_game()
        
    def end_game(self):
        winned_chips = 0
        for player in self.winners:
            player_max_earned_chips = player.nested_chips * len(self.players)
            if player_max_earned_chips >= self.table.bank / len(self.winners):
                player.stack += self.table.bank / len(self.winners)
                winned_chips += self.table.bank / len(self.winners)
                player.nested_chips = 0
            else:
                player.stack += player_max_earned_chips / len(self.winners)
                winned_chips += player_max_earned_chips / len(self.winners)
                player.nested_chips = 0
                
        for player in self.players:
            if player not in self.winners:
                cashback = player.nested_chips - winned_chips / len(self.players)
                if cashback > 0:
                    player.stack += cashback
                    
            player.nested_chips = 0
            player.hand = []
            player.fold = False
            player.combo = None
            player.combo_heuristic = None
        
        self.round = 0
        self.table = None
        self.rating = []
        self.winners = []
        
        
        
        
            
    
            