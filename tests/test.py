import sys, os; sys.path.insert(0, os.path.join(os.getcwd(), ''))
from icecream import ic
from functools import wraps
from __init__  import *
import re
from abc import ABC, ABCMeta, abstractmethod
 
from functools import wraps



log = """[INFO] 26/09/24 16:50:19 Reactions cog is ready [cogs.reactionscog]
[INFO] 26/09/24 16:50:19 Search cog is ready [cogs.searchcog]
[INFO] 26/09/24 16:50:19 TeammateCog cog is ready [cogs.teammatecog]
[INFO] 26/09/24 16:50:19 TheBestChannelCog cog is ready [cogs.thechannelcog]
[INFO] 26/09/24 16:50:19 WeekThread cog is ready [cogs.weekthreadcog]
[INFO] 26/09/24 16:50:19 Log cog is ready [__main__]
[INFO] 26/09/24 16:50:19 Text cog is ready [__main__]
[INFO] 26/09/24 16:50:20 WeekThread date was checked [cogs.weekthreadcog]
[INFO] 26/09/24 17:04:28 Anon cog is ready [cogs.anonmessagecog]
[INFO] 26/09/24 17:04:28 Cat cog is ready [cogs.catcog]
[INFO] 26/09/24 17:04:28 Coup cog is ready [cogs.coupcog]
[INFO] 26/09/24 17:04:28 GamesCog cog is ready [cogs.gamescog]
[INFO] 26/09/24 17:04:28 Reactions cog is ready [cogs.reactionscog]
[INFO] 26/09/24 17:04:28 Search cog is ready [cogs.searchcog]
[INFO] 26/09/24 17:04:28 TeammateCog cog is ready [cogs.teammatecog]
[INFO] 26/09/24 17:04:28 TheBestChannelCog cog is ready [cogs.thechannelcog]
[INFO] 26/09/24 17:04:28 WeekThread cog is ready [cogs.weekthreadcog]
[INFO] 26/09/24 17:04:28 Log cog is ready [__main__]
[INFO] 26/09/24 17:04:28 Text cog is ready [__main__]
[INFO] 26/09/24 17:04:29 WeekThread date was checked [cogs.weekthreadcog]
[INFO] 26/09/24 16:50:19 Reactions cog is ready [cogs.reactionscog]
[INFO] 26/09/24 16:50:19 Search cog is ready [cogs.searchcog]
[INFO] 26/09/24 16:50:19 TeammateCog cog is ready [cogs.teammatecog]
[INFO] 26/09/24 16:50:19 TheBestChannelCog cog is ready [cogs.thechannelcog]
[INFO] 26/09/24 16:50:19 WeekThread cog is ready [cogs.weekthreadcog]
[INFO] 26/09/24 16:50:19 Log cog is ready [__main__]
[INFO] 26/09/24 16:50:19 Text cog is ready [__main__]
[INFO] 26/09/24 16:50:20 WeekThread date was checked [cogs.weekthreadcog]
[INFO] 26/09/24 17:04:28 Anon cog is ready [cogs.anonmessagecog]
[INFO] 26/09/24 17:04:28 Cat cog is ready [cogs.catcog]
[INFO] 26/09/24 17:04:28 Coup cog is ready [cogs.coupcog]
[INFO] 26/09/24 17:04:28 GamesCog cog is ready [cogs.gamescog]
[INFO] 26/09/24 17:04:28 Reactions cog is ready [cogs.reactionscog]
[INFO] 26/09/24 17:04:28 Search cog is ready [cogs.searchcog]
[INFO] 26/09/24 17:04:28 TeammateCog cog is ready [cogs.teammatecog]
[INFO] 26/09/24 17:04:28 TheBestChannelCog cog is ready [cogs.thechannelcog]
[INFO] 26/09/24 17:04:28 WeekThread cog is ready [cogs.weekthreadcog]
[INFO] 26/09/24 17:04:28 Log cog is ready [__main__]
[INFO] 26/09/24 17:04:28 Text cog is ready [__main__]
[INFO] 26/09/24 17:04:29 WeekThread date was checked [cogs.weekthreadcog]
[INFO] 26/09/24 16:50:19 Reactions cog is ready [cogs.reactionscog]
[INFO] 26/09/24 16:50:19 Search cog is ready [cogs.searchcog]
[INFO] 26/09/24 16:50:19 TeammateCog cog is ready [cogs.teammatecog]
[INFO] 26/09/24 16:50:19 TheBestChannelCog cog is ready [cogs.thechannelcog]
[INFO] 26/09/24 16:50:19 WeekThread cog is ready [cogs.weekthreadcog]
[INFO] 26/09/24 16:50:19 Log cog is ready [__main__]
[INFO] 26/09/24 16:50:19 Text cog is ready [__main__]
[INFO] 26/09/24 16:50:20 WeekThread date was checked [cogs.weekthreadcog]
[INFO] 26/09/24 17:04:28 Anon cog is ready [cogs.anonmessagecog]
[INFO] 26/09/24 17:04:28 Cat cog is ready [cogs.catcog]
[INFO] 26/09/24 17:04:28 Coup cog is ready [cogs.coupcog]
[INFO] 26/09/24 17:04:28 GamesCog cog is ready [cogs.gamescog]
[INFO] 26/09/24 17:04:28 Reactions cog is ready [cogs.reactionscog]
[INFO] 26/09/24 17:04:28 Search cog is ready [cogs.searchcog]
[INFO] 26/09/24 17:04:28 TeammateCog cog is ready [cogs.teammatecog]
[INFO] 26/09/24 17:04:28 TheBestChannelCog cog is ready [cogs.thechannelcog]
[INFO] 26/09/24 17:04:28 WeekThread cog is ready [cogs.weekthreadcog]
[INFO] 26/09/24 17:04:28 Log cog is ready [__main__]
[INFO] 26/09/24 17:04:28 Text cog is ready [__main__]
[INFO] 26/09/24 17:04:29 WeekThread date was checked [cogs.weekthreadcog]"""



pages = TextPaginator.prepare_for_paginate(log)

#pag = TextPaginator(ctx, pages)

#async def main():
    #await pag.paginate()
    
#print(pages)

print(pages)
