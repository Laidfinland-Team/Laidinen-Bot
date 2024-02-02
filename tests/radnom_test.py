import random

pidor = 0

nepidor = 0

i=0
while i < 100:
    if a := random.randint(0, 5):
       print(a)
       nepidor += 1
    i += 1
    
print(pidor, nepidor, 100/nepidor)