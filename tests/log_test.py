import sys 
import os
sys.path.insert(0, os.path.join(os.getcwd(), ''))

from __init__ import *

log = Logger("log.log")

log.error("This is an error message")
log.info("This is an info message")
log.warning("This is a warning message")