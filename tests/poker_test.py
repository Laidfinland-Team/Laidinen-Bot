import sys, os; sys.path.insert(0, os.path.join(os.getcwd(), ''))
from ds_poker.simple_poker import Game, Player
from icecream import ic
import poker
import PokerPy

global_players = [Player("SB"), Player("BB")]


            
def test():
    game = Game(global_players, 2)
    game.new_game()
    for player in global_players:
        print(player.hand)
    game.next_round()
    game.next_round()
    game.next_round()
    game.next_round()
    game.next_round()
 
    
    
        
if __name__ == "__main__":
    test()
