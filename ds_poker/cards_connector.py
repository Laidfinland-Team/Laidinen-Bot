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
                self.board_cards.append(Image.open(r".\ds_poker\\images\cards\\" + board[card] + ".png"))
            except:
                self.board_cards.append(Image.open(r".\ds_poker\\images\cards\back_red.png"))

    # Calculate the total width of the concatenated image
    def __call__(self):
        name = ""
        total_width = 0
        for card in self.board_cards:
            total_width += card.width

        # Create a new blank image with the calculated width and the maximum height of the input images
        concatenated_image = Image.new("RGB", (total_width, max(card.height for card in self.board_cards)))

        # Paste the input images onto the concatenated image
        for i, card in enumerate(self.board_cards):
            concatenated_image.paste(card, (i * card.width, 0))
        
        for card in self.board:
            name += card
            
        if name == "":
            name = "empty"
            
        concatenated_image.save(rf".\ds_poker\images\boards\{name}.png", "PNG")

        # Save the concatenated image
        return name