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
    playersMatch = re.findall(".*?[\|=]pn\|(.*?)\|", url)
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
    print (parse("https://www.bridgebase.com/tools/handviewer.html?lin=st||pn|PSMartin,~Mwest,~Mnorth,~Meast|md|2SAK5HKT43DK7CAK62,SJ962H9DQ984CT754,SQ73HAQJ52DAJ5CJ9,ST84H876DT632CQ83|sv|n|rh||ah|Board%2012|mb|P|mb|1N|an|notrump%20opener.%20Could%20have%205M.%20--%202-5%20!C;%202-5%20!D;%202-5%20!H;%202-5%20!S;%2015-17%20HCP;%2018-%20total%20points|mb|P|mb|2C|an|Stayman%20--%20%20|mb|P|mb|2H|an|2-5%20!C;%202-5%20!D;%204-5%20!H;%202-4%20!S;%2015-17%20HCP;%2018-%20total%20points|mb|P|mb|3S!|an|forcing%20H%20raise%20--%202+%20!C;%202+%20!D;%204+%20!H;%2015+%20total%20points|mb|P|mb|4D|an|Cue%20bid%20--%202-5%20!C;%202-5%20!D;%204-5%20!H;%202-4%20!S;%2015-17%20HCP;%20no%20!CA;%20!DA;%2018-%20total%20points|mb|P|mb|4N|an|Blackwood%20(H)%20--%202+%20!C;%202+%20!D;%204+%20!H;%2017+%20total%20points|mb|P|mb|5S|an|Two%20or%20five%20key%20cards;%20queen%20--%202-5%20!C;%202-5%20!D;%204-5%20!H;%202-4%20!S;%2015-17%20HCP;%20no%20!CA;%20!DA;%20!HQ;%2018-%20total%20points|mb|P|mb|7H|an|2+%20!C;%202+%20!D;%204+%20!H;%2021+%20total%20points|mb|P|mb|P|mb|P|pc|S4|pc|SA|pc|S2|pc|S3|pc|HK|pc|H9|pc|H2|pc|H6|mc|13|"))
