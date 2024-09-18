import os as _os

def cls():
    _os.system('cls')
    

def tryParseString(string):
    try:
        return str(string)
    except ValueError:
        return False
    
def tps(string):
    return tryParseString(string)
    

def tryParseInt(string):
    try:
        return int(string)
    except ValueError:
        return False
    
def tpi(string):
    return tryParseInt(string)
    
    
def tryParseFloat(string):
    try:
        return float(string)
    except ValueError:
        return False
    
def tpf(string):
    return tryParseFloat(string)
    
    
    
def check_for_numbers(number):
    number = type(number)
    result = True if number is int or number is float else False
    return result

def cfn(number):
    return check_for_numbers(number)

def check_for_string(string):
    string = type(string)
    result = True if string is str else False
    return result

def cfs(string):
    return check_for_string(string)


def check_for_bool(boolean):
    boolean = type(boolean)
    result = True if boolean is bool else False
    return result

def cfb(boolean):
    return check_for_bool(boolean)


def check_for_custom_string(args, arg):
    result = True if arg in args else False
    return result

def cfcs(args, arg):
    return check_for_custom_string(args, arg)


def hide (string):
    return string.replace(string, '■' * len(string))

