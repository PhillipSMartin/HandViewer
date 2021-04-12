# -*- coding: utf-8 -*-
"""
This method takes a BBO handviewer url, parses it, and returns a dictionary with deal info in the following format:
    {
        "Board number": <integer>
        "Dealer": <"North", "South", "East", or "West" >
        "Auction": <a list of calls eg. ['1C', 'D', 'R', '3N', 'P', 'P', 'P'] >
        "Seats": [ 
                    { "Player": <player's name>',
                      "Direction":  <"North", "South", "East", or "West" >
                        "Hand": 
                            { "Spades": <string, using AKQJT for honors>
                              "Hearts": <string, using AKQJT for honors>
                              "Diamonds": <string, using AKQJT for honors>
                              "Clubs": <string, using AKQJT for honors>
                            }
                    },
                    ...
                ]
      }
"""

import re
import sys
from typing import List
import globals

globals.initialize()

    
def splitSuits(hand: str):
    # input 'S96432HKQ94DT5C73' (possibly with an integer preceding the S)
    # output ['96432', 'KQ9', 'T5', '73']
    return re.split('[SHDC]', hand)[1:]

def buildHand(suitList: List[str]):
    # input ['96432', 'KQ9', 'T5', '73']
    # output {'Spades': '96432', 'Hearts': 'KQ94', 'Diamonds': 'T5', 'Clubs': '73'}
    assert len(suitList) == 4, "Invalid input to buildHand method"
    return dict(zip(globals.suits, suitList))
 
def main(url: str):
    # extract board number
    boardMatch = re.findall(".*?Board%20(.*?)\|", url)
    assert len(boardMatch) > 0, "No board number"
    boardNumber = int(boardMatch[0])
    
    # extract string containing each hand, separated by commas
    # build a list with one item for each hand
    handsMatch = re.findall(".*?\|md\|(.*?)\|", url)
    assert len(handsMatch) > 0, "No hands"
    hands = handsMatch[0].split(',')
   
    # first char of first hand is dealer: 1 for West, 2 for North, etc.
    #   subtract 1 to make it an index into globals.directions
    dealer = int(handsMatch[0][0]) - 1
    
    # extract string containing players' names
    # build a list with one item for each player
    # players whose names start with ~ are robots
    playersMatch = re.findall(".*?\|pn\|(.*?)\|", url)
    assert len(playersMatch) > 0, "No players"
    players = playersMatch[0].split(',')
    for i in range(len(players)):
        if players[i][0] == '~':
            players[i] = 'Robot'
     
    # extract auction
    # build a list of calls, e.g. ['1C', 'P', '2C', 'P', '2S', 'P', '3N', 'P', 'P', 'P']
    auction = re.findall('mb\|([1-7SHDCNRP]+)[!\|]', url)
    assert len(auction) > 0, "No auction"
    
    # combine players names, directions, and hands into a list of tuples
    # example of an item in the list: ('PSMartin', 'South', {'Spades': 'T5', 'Hearts': 'AJ7', 'Diamonds': 'KQJ2', 'Clubs': 'AJT6'})
    directionsSouthFirst = globals.directions[globals.directions.index('South'):] + globals.directions[:globals.directions.index('South')]
    handsZip = zip(players, directionsSouthFirst, [buildHand(splitSuits(hand)) for hand in hands])
    # convert list of tuples into a list of dictionaries
    handsList = [dict(zip(["Player", "Direction", "Hand"], item)) for item in handsZip]
    
   # handsDict = dict(zip(globals.directions[-1:] + globals.directions[:3], [dict(zip(["Player", "Hand"], item)) for item in handsZip]))
    
    # combine all the above into into a single dictionary
    
    return  { "Board number" : boardNumber,
                 "Dealer" : globals.directions[dealer],
                 "Auction" : auction,
                 "Seats" : handsList
             }
              
    
    
    
if len(sys.argv) > 1:
    main(sys.argv[1])
else:
    # for testing
    print (main("https://www.bridgebase.com/tools/handviewer.html?lin=st||pn|PSMartin,~Mwest,~Mnorth,~Meast|md|3ST5HAJ7DKQJ2CAJT6,S96432HKQ94DT5C73,SAK7HT32D98CKQ852,SQJ8H865DA7643C94|sv|o|rh||ah|Board%201|mb|1C|an|Minor%20suit%20opening%20--%203+%20!C;%2011-21%20HCP;%2012-22%20total%20points|mb|P|mb|2C!|an|Inverted%20minor%20suit%20raise%20--%204+%20!C;%203-%20!H;%203-%20!S;%2010+%20HCP;%20forcing%20to%202N|mb|P|mb|2S|an|3+%20!C;%2011-21%20HCP;%2012-22%20total%20points;%20stop%20in%20!S;%20forcing|mb|P|mb|3N|an|4+%20!C;%203-%20!H;%203-%20!S;%2014-18%20HCP;%20partial%20stop%20in%20!D;%20partial%20stop%20in%20!H|mb|P|mb|P|mb|P|pc|S3|pc|SA|pc|SQ|pc|S5|pc|D9|pc|D3|pc|DQ|pc|D5|pc|CA|pc|C3|pc|C2|pc|C4|pc|CJ|pc|C7|pc|CK|pc|C9|pc|D8|pc|D7|pc|DK|pc|DT|pc|C6|pc|H9|pc|C8|pc|H5|pc|CQ|pc|H8|pc|CT|pc|S6|pc|C5|pc|D6|pc|D2|pc|S9|pc|H2|pc|H6|pc|HJ|pc|HQ|pc|H4|pc|H3|pc|D4|pc|H7|pc|HA|pc|HK|pc|HT|pc|DA|mc|12|"))
