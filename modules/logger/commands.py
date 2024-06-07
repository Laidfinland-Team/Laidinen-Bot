from datetime import datetime
from colorama import Fore, Back, Style


def custom_print(message: str):
    print(message)
    with open("../../log.log", "w") as file:
        file.write(message)

def formatted_datetime():
    formatted_datetime = datetime.now().strftime('%d/%m/%y %H:%M:%S')
    return formatted_datetime

def error(message):
    custom_print(Fore.RED + Style.BRIGHT + "[ERROR] " + f"{formatted_datetime()} " + Style.DIM + message + Style.RESET_ALL)
    
def info(message):
    custom_print(Fore.BLUE + Style.BRIGHT + "[INFO] " + f"{formatted_datetime()} " + Style.DIM + message + Style.RESET_ALL)
    
def warning(message):
    custom_print(Fore.YELLOW + Style.BRIGHT + "[WARNING] " + f"{formatted_datetime()} " + Style.DIM  + message + Style.RESET_ALL)
    

def output(message: str, channel: str = "None"):
    custom_print(Fore.GREEN + Style.BRIGHT + "[OUTPUT] "+ f"{formatted_datetime()} " + f"{channel.name}: " + Style.DIM + message + Style.RESET_ALL)
