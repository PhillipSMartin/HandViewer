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

#import sys
import re
import globals

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
    print (parse("https://www.bridgebase.com/tools/handviewer.html?bbo=y&lin=st%7C%7Cmd%7C4SAKT92HA4D3CKQJ85%2CSQ83HKJ953DA742C9%2CS6H862DKQJT5CA743%2CSJ754HQT7D986CT62%7Csv%7CN%7Cah%7CBoard%202%7Cmb%7CP%7Cmb%7C1S%7Can%7CMajor%20suit%20opening%20--%205%2B%20%21S%3B%2011-21%20HCP%3B%2012-22%20total%20points%7Cmb%7CP%7Cmb%7C1N%7Can%7CForcing%20one%20notrump%20--%203-%20%21S%3B%206%2B%20HCP%3B%2012-%20total%20points%7Cmb%7CP%7Cmb%7C2C%7Can%7CNew%20suit%20--%203%2B%20%21C%3B%203-%20%21H%3B%205%2B%20%21S%3B%2011%2B%20HCP%3B%2012-18%20total%20points%7Cmb%7CP%7Cmb%7C2N%7Can%7CBalanced%20invite%20--%204-%20%21C%3B%202-%20%21S%3B%2010%2B%20HCP%3B%2012-%20total%20points%7Cmb%7CP%7Cmb%7C3N%7Can%7C3%2B%20%21C%3B%203-%20%21H%3B%205-6%20%21S%3B%2015%2B%20HCP%3B%2018-%20total%20points%3B%20partial%20stop%20in%20%21D%3B%20partial%20stop%20in%20%21H%7Cmb%7CP%7Cmb%7CP%7Cmb%7CP%7Cpc%7CD6%7Cpc%7CD3%7Cpc%7CDA%7Cpc%7CD5%7Cpc%7CH3%7Cpc%7CH2%7Cpc%7CH7%7Cpc%7CHA%7Cmc%7C12%7C"))
