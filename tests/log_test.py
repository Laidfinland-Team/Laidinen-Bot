import sys 
import os
sys.path.insert(0, os.path.join(os.getcwd(), ''))

import traceback

from __init__ import *

log = Logger("log.log") # Initialize the Logger object 

try:
    print(dsasd) # Error

except Exception as e:
    log.error("Test error message", e) # Detailed log the error
    log.info("This is an info message") # Log the informational message
    log.warning("This is a warning message") # Log the warning message
log.error("Test error message") # Log the error message