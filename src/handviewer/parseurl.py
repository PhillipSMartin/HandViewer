# -*- coding: utf-8 -*-
"""
The parse method of this module takes a BBO handviewer url, parses it, and returns a dictionary with deal info in the following format:
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

import globals
import re

globals.initialize()
    
def splitSuits(hand: str) -> list:
    # input 'S96432HKQ94DT5C73' (possibly with an integer preceding the S)
    # output ['96432', 'KQ9', 'T5', '73']
    return re.split('[SHDC]', hand)[1:]

def extractBoardNumber(url: str) -> int:
    boardMatch = re.findall(".*?Board(.*?)\|", url)
    if len(boardMatch) == 0:
        return 0
    else:
        return int(boardMatch[0][-2:])

def extractDealer(hand: str) -> int:
    # first char of hand is dealer: 1 for South, 2 for West, etc.
    #   subtract 2 to make it an index into globals.directions
    return (int(hand[0]) - 2) % 4
 
def extractHands(url: str) -> list:
    # extract string containing each hand, separated by commas
    # build a list with one item for each hand
    handsMatch = re.findall(".*?\|md\|(.*?)\|", url)
    assert len(handsMatch) > 0, "No hands"
    return handsMatch[0].split(',')
 
def extractPlayers(url: str) -> list:    
    # extract string containing players' names
    # build a list with one item for each player
    # players whose names start with ~ are robots
    playersMatch = re.findall(".*?\|pn\|(.*?)\|", url)
    assert len(playersMatch) > 0, "No players"
    players = playersMatch[0].split(',')
    for i in range(len(players)):
        if players[i][0] == '~':
            players[i] = 'Robot'
        elif players[i] == 'PSMartin':
            players[i] = 'Phillip'
    return players

def extractAuction(url: str) -> list:
    # build a list of calls, e.g. ['1C', 'P', '2C', 'P', '2S', 'P', '3N', 'P', 'P', 'P']
    auction = re.findall('mb\|([1-7SHDCNRP]+)[!\|]', url)
    assert len(auction) > 0, "No auction"
    return auction

def parse(url: str) -> dict:
    #print('***entering parseurl***')
    #print(f'url:{url}')
    
    boardNumber = extractBoardNumber(url)
    hands = extractHands(url)
    dealer = extractDealer(hands[0])
    players = extractPlayers(url)
    auction = extractAuction(url)
    
    # combine players names, directions, and hands into a list of tuples
    # example of an item in the list: ('PSMartin', 'South', {'Spades': 'T5', 'Hearts': 'AJ7', 'Diamonds': 'KQJ2', 'Clubs': 'AJT6'})
    directionsSouthFirst = globals.directions[globals.directions.index('South'):] + globals.directions[:globals.directions.index('South')]
    handsZip = zip(players, directionsSouthFirst, [globals.buildHand(splitSuits(hand)) for hand in hands])
    
    # convert list of tuples into a list of dictionaries
    handsList = [dict(zip(["Player", "Direction", "Hand"], item)) for item in handsZip]
    
    # combine all the above into into a single dictionary
    return  { "Board number" : boardNumber,
                 "Dealer" : globals.directions[dealer],
                 "Auction" : auction,
                 "Seats" : handsList
             }
 
# for testing          
if __name__ == '__main__': 
    print (parse("https://www.bridgebase.com/tools/handviewer.html?lin=st||pn|PSMartin,~Mwest,~Mnorth,~Meast|md|1SQJ8HKQJDKT72CT84,SAHT953DQ5CKQJ752,SKT9765H642D43C93,S432HA87DAJ986CA6|sv|e|rh||ah|Board%203|mb|P|mb|1C|an|Minor%20suit%20opening%20--%203+%20!C;%2011-21%20HCP;%2012-22%20total%20points|mb|P|mb|1D|an|One%20over%20one%20--%204+%20!D;%206+%20total%20points|mb|P|mb|1H|an|3+%20!C;%204+%20!H;%2011+%20HCP;%2012-18%20total%20points|mb|P|mb|1S!|an|Fourth%20suit%20forcing%20--%204+%20!D;%203-%20!S;%2012+%20HCP;%2013+%20total%20points;%20forcing%20to%203N|mb|P|mb|1N|an|3+%20!C;%204+%20!H;%202-3%20!S;%2011-14%20HCP;%2012+%20total%20points;%20partial%20stop%20in%20!S;%20forcing%20to%203N|mb|P|mb|2H|an|4+%20!D;%204+%20!H;%203-%20!S;%2012+%20HCP;%2013+%20total%20points;%20forcing%20to%203N|mb|P|mb|4H|an|3+%20!C;%204+%20!H;%202-3%20!S;%2011+%20HCP;%2012-14%20total%20points;%20partial%20stop%20in%20!S|mb|P|mb|P|mb|P|pc|D4|pc|D6|pc|DK|pc|D5|pc|SQ|pc|SA|pc|S7|pc|S2|pc|H3|pc|H4|pc|H8|pc|HJ|pc|S8|pc|H5|pc|ST|pc|S3|pc|HT|pc|H6|pc|H7|pc|HQ|pc|D2|pc|DQ|pc|D3|pc|D8|pc|C2|pc|C9|pc|CA|pc|C4|pc|HA|pc|HK|pc|H9|pc|H2|pc|C6|pc|C8|pc|CK|pc|C3|pc|CQ|pc|S9|pc|D9|pc|CT|pc|CJ|pc|S5|pc|DA|pc|D7|pc|C7|pc|S6|pc|S4|pc|DT|pc|C5|pc|SK|pc|DJ|pc|SJ|"))
