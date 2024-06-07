from ds_poker.ds_poker import Game, Player
from icecream import ic
import poker
import PokerPy

global_players = [Player("SB"), Player("BB"), Player("BTN"), Player("UTG"), Player("UTG+1")]


            
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
    print(game.table.board)
 
    
    
        
if __name__ == "__main__":
    test()
