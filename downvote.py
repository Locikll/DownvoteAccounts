"""
This bot downvotes compromised/blacklisted accounts
Written by @Locikll

"""
import sys
import datetime
import os
import subprocess
import math
import re
from time import gmtime, strftime
import os.path
import timeit

from contextlib import suppress

from langdetect import detect


import multiprocessing.dummy as mp 

import piston
from piston.steem import Steem
from random import randint
import steem as pysteem

# EDITABLE VARIABLES {

#The account to downvote with
Downvoteacc = 'pfunk'
steemPostingKey = ''

#Compromised accounts and downvote weight
Compromisedaccs = ['birjudanak', 'sallybeth23', 'rolf.bakker', 'danyfay']
Downvoteweight = 0.10  #Measured in SBD

Historylimit = 50 #Account history limit for flagging comments

# }


Nodes = ["wss://this.piston.rocks","wss://steemd.steemit.com"]

tic = timeit.default_timer()

steem = Steem(wif=steemPostingKey,node=Nodes[0])

#calculate sbd per mvests
conv = pysteem.account.Account(Downvoteacc).converter

steemtoMvest = conv.steem_per_mvests()


accMvest = steem.get_balances(Downvoteacc)['vesting_shares_steem'].amount

voteSBD = accMvest / (20*steemtoMvest)

voteweight = Downvoteweight / voteSBD * 100

print(voteweight)

if voteweight < 0.01:
    voteweight = 0.01
    
def voting():
    
    for compacc in range(0,len(Compromisedaccs)):
    
        
        #For posts
        recentpost = steem.get_blog(Compromisedaccs[compacc])[0] 
        activepostvotes = recentpost.active_votes  
        hasvoted = list(filter(lambda voter: voter['voter'] == Downvoteacc,activepostvotes))
        
        if hasvoted == []:
            try:
                steem.vote(identifier=recentpost.identifier,weight=((-1)*voteweight))
            except Exception as e:
                print(str(e))
                pass            

        #For comments
        Comments = list(pysteem.account.Account(Compromisedaccs[compacc]).get_account_history(filter_by='comment',limit=Historylimit,index=-1,order=1))
    
        for dwnv in range(0,len(Comments)):
            
            postauthor = Comments[dwnv]['parent_author']
            permlink = Comments[dwnv]['permlink']
            author = Compromisedaccs[compacc]
            identifier = '@'+author+'/'+permlink
            
            try:
                comm = steem.get_post(identifier)
                hasvoted = list(filter(lambda voter: voter['voter'] == Downvoteacc,comm.active_votes))
            except Exception as e:
                hasvoted = ['error']
                print(str(e))
                pass       
        
            if postauthor == author and hasvoted==[]:
                
                try:
                    steem.vote(identifier=identifier,weight=((-1)*voteweight))
                except Exception as e:
                    print(str(e))
                    pass
                
                
                print("Downvoted: "+identifier)

#print(voteweight)

if __name__ == "__main__":
    while True:
        try:
            voting()
   
        except (KeyboardInterrupt):
            print("Quitting...")
            break
        except Exception as e:
            print(Exception)
            print("### Exception Occurred: Restarting...")
        