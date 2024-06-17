from cogs.word_game import *
from __init__ import *


class Game:
    def __init__(self):
        """
        Initialize the game with a spell checker, database connection, and cursor.
        Create a table named 'words' if it doesn't exist.
        """
        self.spell = SpellChecker(language='ru')
        self.db = sqlite3.connect("game_word.db")
        self.cur = self.db.cursor()
        self.cur.execute("""CREATE TABLE IF NOT EXISTS words(word TEXT);
                        """)
        self.db.commit()

    def __del__(self):
        """
        Close the database connection when the game object is destroyed.
        """
        self.db.close()
    
    async def CheckWord(self, word: str) -> int:
        """
        Check if a word is spelled correctly, unique, and ends with the last symbol.

        Parameters:
        word (str): The word to check.

        Returns:
        int: 0 if the word is not spelled correctly, 1 if it is spelled correctly, unique, and ends with the last symbol,
             2 if it is spelled correctly and unique but doesn't end with the last symbol,
             3 if it is spelled correctly but not unique.
        """
        print(self.spell.known([word]))
        if len(self.spell.known([word])) != 0:
            self.cur.execute(f"SELECT word FROM words WHERE word LIKE '%{word}%'")
            if word[-1] != await self.GetLastSymbol():
                return 3
            elif len(self.cur.fetchall()) > 0:
                return 2
            self.db.commit()
            return 1
        return 0
    
    async def AddWord(self, word: str):
        """
        Add a word to the database.

        Parameters:
        word (str): The word to add.
        """
        self.cur.execute(f"""INSERT INTO words(word) 
                    VALUES('{word}');""")
        self.db.commit()
    
    async def AddLastSymbol(self, symbol: str):
        """
        Add the last symbol to a file.

        Parameters:
        symbol (str): The last symbol.
        """
        with open("last_symbol.lsb", "w") as f:
            f.write(symbol);
    
    async def GetLastSymbol(self):
        """
        Get the last symbol from a file.

        Returns:
        str: The last symbol.
        """
        if os.path.exists("last_symbol.lsb"):
            with open("last_symbol.lsb", "r") as f:
                return f.read();
        else: 
            return "";