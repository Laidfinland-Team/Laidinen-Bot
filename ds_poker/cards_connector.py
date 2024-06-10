from PIL import Image
from icecream import ic

# Open the five images


class Board:
    def __init__(self, board):
        self.board = board
        self.board_cards = []
        for card in range(0, 5):
            try:
                board[card]
                self.board_cards.append(Image.open(r".\ds_poker\\images\cards\\" + str(board[card]).split(":")[1].strip().replace("♠", "S").replace("♥", "H").replace("♣", "C").replace("♦", "D") + ".png"))
            except:
                self.board_cards.append(Image.open(r".\ds_poker\\images\cards\back_red.png"))

    # Calculate the total width of the concatenated image
    def __call__(self):
        name = ""
        total_width = 0
        for card in self.board_cards:
            total_width += card.width

        # Create a new blank image with the calculated width and the maximum height of the input images
        concatenated_image = Image.new("RGBA", (total_width, max(card.height for card in self.board_cards)))

        # Paste the input images onto the concatenated image
        for i, card in enumerate(self.board_cards):
            concatenated_image.paste(card, (i * card.width, 0))
        
        for card in self.board:
            name += str(card).split(":")[1].strip().replace("♠", "S").replace("♥", "H").replace("♣", "C").replace("♦", "D")
            
        if name == "":
            name = "empty"
        
        concatenated_image = concatenated_image.resize((concatenated_image.width * 2, concatenated_image.height * 2 ), Image.Resampling.NEAREST)
        concatenated_image.save(rf".\ds_poker\images\boards\{name}.png", "PNG")

        # Save the concatenated image
        return name
    
class Hand:
    def __init__(self, hand):
        self.hand = hand
        self.hand_cards = []
        for card in range(0, 2):
            self.hand_cards.append(Image.open(r".\ds_poker\\images\cards\\" + str(hand[card]).split(":")[1].strip().replace("♠", "S").replace("♥", "H").replace("♣", "C").replace("♦", "D") + ".png"))

    # Calculate the total width of the concatenated image
    def __call__(self):
        name = ""
        total_width = 0
        for card in self.hand_cards:
            total_width += card.width

        # Create a new blank image with the calculated width and the maximum height of the input images
        concatenated_image = Image.new("RGBA", (total_width, max(card.height for card in self.hand_cards)))

        # Paste the input images onto the concatenated image
        for i, card in enumerate(self.hand_cards):
            concatenated_image.paste(card, (i * card.width, 0))
        
        for card in self.hand:
            name += str(card).split(":")[1].strip().replace("♠", "S").replace("♥", "H").replace("♣", "C").replace("♦", "D")
            
        if name == "":
            name = "empty"
            
        concatenated_image = concatenated_image.resize((concatenated_image.width * 2, concatenated_image.height * 2 ), Image.Resampling.NEAREST)
        concatenated_image.save(rf".\ds_poker\images\hands\{name}.png", "PNG")

        # Save the concatenated image
        return name