import poker
import PokerPy
import random
from icecream import ic

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
    def __init__(self, cards):
        self.cards = cards

    def get_combo(self):
        return PokerPy.get_best_hand(self.cards)
    def hand_heuristic(self):
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
    
    def __repr__(self):
        return self.name
    
    def wait_for_action(self, game):
        table = game.table
        if self.round_chips < table.last_bet:
            action = poker_input(f"{self.name}, amount to call {table.last_bet - self.round_chips} enter your action:[fold/call/raise]", ["fold", "call","raise"], game)
        else:
            action = poker_input(f"{self.name}, enter your action:[fold/check/raise]", ["fold", "check","raise"], game)
        match action.split()[0]:
            case "fold":
                self.fold = True
                return "fold"
            case "check":
                return "check"
            case "call":
                return "call", float(game.table.last_bet - self.round_chips)
            case "raise":
                return "raise", float(action.split()[1])
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
    def __init__(self, players, big_blind):
        self.small_blind = big_blind / 2
        self.big_blind = big_blind
        self.players = players
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
    
    def round_cycle(self):
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
                        self.bet(player, self.small_blind)
                        continue
                    elif i == 1:
                        self.bet(player, self.big_blind)
                        continue
                elif self.round == 0 and not first_cycle:
                    if i > 1:
                        break
                    
                        
                action = player.wait_for_action(self)
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
        
    def next_round(self):
        for player in self.players:
            player.round_chips = 0
        match self.round:
            case 0:
                pass
            case 1:
                for card in self.table.flop:
                    self.table.board.append(card)
                print(self.table.board)
            case 2:
                self.table.board.append(self.table.turn)
                print(self.table.board)
            case 3:
                self.table.board.append(self.table.river)
                print(self.table.board)
            case _:
                return self.determinate_winner()
                
        self.round_cycle()
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
                player.combo = ic(player_combo)
                player.combo_heuristic = ic(player_combo.hand_heuristic())
            winners = [player.combo_heuristic for player in self.players if not player.fold]
            winner = max(winners)
            rating = winners.sort()
            winners = []
            for player in self.players:
                if player.combo_heuristic == winner and not player.fold:
                    winners.append(player)
            self.rating = rating
            self.winners = winners
            print(winners)
            self.eng_game()
        
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
        
        
        
        
            
    
            