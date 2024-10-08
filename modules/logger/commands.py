from datetime import datetime
from colorama import Fore, Back, Style
import discord
import traceback
import inspect
from accessify import private
import os
import sys

class Logger:
    """
    @brief A class to log messages to a file and print them to the console.

    @details This class provides methods for logging error, informational, warning, and output messages.
    The messages are printed to the console with appropriate color formatting and written to a file.
    """

    def __init__(self, path: str, printing=True):
        """
        @brief Constructor to initialize the Logger object.

        @param path (str): The path to the log file.
        """
        
        self.file = open(path, "a", errors="ignore", encoding='utf-8')
        self.printing = printing
    
    def __del__(self):
        """
        @brief Destructor to close the log file and write a newline character.
        """

        self.write("\n")
        self.file.close()
    

    @private
    def write(self, message : str):
        """
        @brief Private method to write a message to the log file.

        @param message (str): The message to be written to the log file.
        """

        self.file.write(message + "\n")
        self.file.flush()




        

    @private
    @staticmethod
    def formatted_datetime():
        """
        @brief Private static method to get the current date and time in a formatted way.

        @return formatted_datetime (str): The current date and time in a formatted way.
        """

        formatted_datetime = datetime.now().strftime('%d/%m/%y %H:%M:%S')
        return formatted_datetime

    def white(self, message : str):
        """
        @brief Method to print a white message.

        @param message (str): The message to be printed.
        """

        return Fore.WHITE + Style.NORMAL + message
    
    def security(self, message : str):
        """
        @brief Method to print a security message.

        @param message (str): The message to be printed.
        """

        frame = inspect.currentframe()
        name = frame.f_back.f_back.f_globals['__name__']
        
        if self.printing:
            print(Fore.YELLOW + Style.BRIGHT + '<' + Fore.RED + "SECURITY" + Fore.YELLOW + '>' + Fore.RED + f" {self.formatted_datetime()} " + message + self.white(f" [{name}]") + Style.RESET_ALL)
        self.write("[SECURITY] " + f"{self.formatted_datetime()} " + message + f" [{name}]")
    
    def system(self, message : str):
        """
        @brief Method to print a system message.

        @param message (str): The message to be printed.
        """

        frame = inspect.currentframe()
        name = frame.f_back.f_back.f_globals['__name__']
        
        if self.printing:
            print(Fore.CYAN + Style.BRIGHT + "[SYSTEM] " + f"{self.formatted_datetime()} " + message + self.white(f" [{name}]") + Style.RESET_ALL)
        for s in message:
            if not s.isascii():
                message = message.replace(s, '')
        self.write("[SYSTEM] " + f"{self.formatted_datetime()} " + message + f" [{name}]")
    
    def error(self, message : str, exec: Exception = None):
        """
        @brief Logs an error message to the console and file.

        @details This method prints an error message to the console with appropriate color formatting.
        It also writes the error message to a log file, along with an optional exception traceback.

        @param message (str): The error message to be logged.
        @param exec (Exception, optional): The exception that caused the error. Defaults to None.
        """

        # Output detailed error only if an error is reported
        exec_msg = ""
        if isinstance(exec, Exception):
            exec_msg = traceback.format_exc()
        frame = inspect.currentframe()
        name = frame.f_back.f_back.f_globals['__name__']

        if self.printing:        
            print(Fore.RED + Style.BRIGHT + "[ERROR] " + f"{self.formatted_datetime()} " +  message + self.white(f" [{name}]") + Style.DIM + exec_msg + Style.RESET_ALL)
        self.write("[ERROR] " + f"{self.formatted_datetime()} " + message + f" [{name}]" + exec_msg)
        
    def info(self, message: str):
        """
        @brief Method to print an informational message.

        @param message (str): The informational message to be printed.
        """
        frame = inspect.currentframe()
        name = frame.f_back.f_back.f_globals['__name__']
        
        if self.printing:
            print(Fore.BLUE + Style.BRIGHT + "[INFO] " + f"{self.formatted_datetime()} " + Style.DIM + message + self.white(f" [{name}]") + Style.RESET_ALL)
        self.write("[INFO] " + f"{self.formatted_datetime()} " + message + f" [{name}]")
        
    def warning(self, message: str):
        """
        @brief Method to print a warning message.

        @param message (str): The warning message to be printed.
        """
        frame = inspect.currentframe()
        name = frame.f_back.f_back.f_globals['__name__']
        
        if self.printing:
            print(Fore.YELLOW + Style.BRIGHT + "[WARNING] " + f"{self.formatted_datetime()} " + Style.DIM  + message + self.white(f" [{name}]") +  Style.RESET_ALL)
        self.write("[WARNING] " + f"{self.formatted_datetime()} " + message + f" [{name}]")
        

    def output(self, channel : discord.channel, message : str):
        """
        @brief Method to print and log a message to a Discord channel.

        @param channel (discord.channel): The Discord channel to send the message to.
        @param message (str): The message to be printed and logged.
        """
        frame = inspect.currentframe()
        name = frame.f_back.f_back.f_globals['__name__']
        
        print(Fore.GREEN + Style.BRIGHT + "[OUTPUT] "+ f"{self.formatted_datetime()} " + f"{channel.name if type(channel) != discord.DMChannel else "Direct message"}: " + Style.DIM + message + self.white(f" [{name}]") + Style.RESET_ALL)
        self.write("[OUTPUT] " + f"{self.formatted_datetime()} " + message + f" [{name}]")