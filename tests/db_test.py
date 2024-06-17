import sys 
import os
sys.path.insert(0, os.path.join(os.getcwd(), ''))

from __init__ import *

test_db = db.Database('test.db')
info(str(test_db))