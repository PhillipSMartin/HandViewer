# -*- coding: utf-8 -*-
"""
The build method of this module takes as input a dictionary describing a deal in the following format:
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
        
    it outputs an html string, displaying the deal in a variety of formats
    as specified by the options string
    
    the options string must contain at least one of SWNE and may also contain A
    if it contains only one of SWNE, that hand is formatted on a single line
    if it contains more than one of SWNE, all the specified hands are formatted in a diagram
    
    if in contains A, the auction is formatted below the diagram
    
    if it contains a number, the deal is shifted clockwise that number of positions (and directions are reassigned before formatting)
"""
from typing import Dict, List
import globals
import re

globals.initialize()
pips = { 'S': '&#9824;', 
        'H': '<span style="color: rgb(192, 22, 22);">&#9829;</span>',
        'D': '<span style="color: rgb(192, 22, 22);">&#9830;</span>',
        'C': '&#9827;'
        }


def shift(direction: str, n: int) -> str:
    # returns direction n places clockwise from specified direction
    # shift("South", 1) returns "West"
    return globals.directions[(globals.directions.index(direction) + n) % 4]

def rotateDeal(deal: dict, n: int) -> dict:
    # rotates deal n seats counter-clockwise
    deal["Dealer"] = shift(deal["Dealer"], n)
    for seat in deal['Seats']:
        seat["Direction"] = shift(seat["Direction"], n)
    return deal
    
def formatSuit(suit: str) -> str:
    # input: 'AJT6'
    # output: ' A J 10 6'
    return ' '.join(suit).replace('T','10') or '--'

def formatHand(hand: Dict[str, str], withBreaks: bool = True) -> str:
    # convert dictionary of holdings by suit into an html string displaying the hand
    # input:  {'Spades': 'T5', 'Hearts': 'AJ7', 'Diamonds': 'KQJ2', 'Clubs': 'AJT6'}
    # output: 
    #    '&#9824; 10 5<br />
    #     <span style="color: rgb(192, 22, 22);">&#9829;</span> A J 7<br />
    #     <span style="color: rgb(192, 22, 22);">&#9830;</span> K Q J 2<br />
    #     &#9827; A J 10 6<br />'

    br = '<br />\n' if withBreaks else '&nbsp;&nbsp;'
    suitStr = [pip + ' ' + formatSuit(hand[suit]) for pip, suit in zip(pips.values(), globals.suits)]
    return br.join(suitStr) + br

def formatHandDiagram(handInfo: dict) -> str:
    # convert dictionary of hand info into an html string displaying the direction, player, and hand itself
    # input:  { "Player": "Phillip", "Direction": "North", "Hand": ...}
    # output: 
    #   NORTH<br />
    #   <i>Phillip</i><br />
    #   ♠ A Q 10 7 6<br />
    #   <span style="color: #c01616;">♥</span> A J 7 5 4<br />
    #   <span style="color: #c01616;">♦</span> 10 3<br />
    #   ♣ 6<br />
    # 
    
    diagram =  f'{handInfo["Direction"].upper()}<br />\n'
    if "Player" in handInfo:
        diagram += f'<i>{handInfo["Player"]}</i><br />\n'
    if "Hand" in handInfo:
        diagram += f'{formatHand(handInfo["Hand"])}\n'
    return diagram
    
    
def formatHandDiagrams(hands: dict, withBreaks: bool = True) -> dict:
    # convert list of hands into a dictionary of hand diagrams, keyed by direction
     
    return dict([(hand['Direction'], formatHandDiagram(hand)) for hand in hands])

def formatCall(call: str) -> str:
    # convert abbreviation into a displayable html string
    # input: '1C'
    # output: '1 &#9827;</span>'
    for suit, pip in pips.items():
        if len(call) > 1:
            call = call.replace(suit, ' ' + pip)
    return call.replace('P', 'Pass').replace('D', 'Double').replace('R', 'Redouble').replace('N', ' NT')

def formatAuctionCalls(auction: List[str], dealer: str) -> list:
    # convert list of call  abbreviations into a  list of displayable calls with the first call being West
    # input: ['1C', 'Pass', '2C', 'Pass', '2S', 'Pass', '3 NT', 'Pass', 'Pass', 'Pass'], North dealer
    # output: [' ', '1 &#9827;', 'Pass', '2 &#9827;',
    #     'Pass', '2 &#9824;', 'Pass', '3 NT', 
    #     '(All pass)']
        
    # translate abbreviations to full calls
    callList = [formatCall(call) for call in auction]
    
    # replace three or four final passes with (All pass)
    if len(callList) > 3:
        if callList[-3:] == ['Pass', 'Pass', 'Pass']:
            callList[-3:] = ['(All pass)']
        if callList[-1] == 'Pass':
            del callList[-1]
         
    # determine how many empty cells should begin the auction
    newAuction = ([' '] * ((globals.directions.index(dealer)) % 4))
    newAuction.extend(callList)
    return newAuction

def formatAuctionHeader(deal: dict) -> str:
    # contruct auction heading from list of players (West first)
    # input: each player's name can be found in deal[direction]["PLayer"]
    # output: 
    # <tr>
    #    <td align="left" width="25%"><b>West</b></td>
    #    <td align="left" width="25%"><b>North</b></td>
    #    <td align="left" width="25%"><b>East</b></td>
    #    <td align="left" width="25%"><b>South</b></td>
    # </tr>
    # <tr>
    #    <td align="left" width="25%"><i>Robot</i></td>
    #    <td align="left" width="25%"><i>Robot</i></td>
    #    <td align="left" width="25%"><i>Robot</i></td>
    #    <td align="left" width="25%"><i>Phillip</i></td>
    # </tr>
    players = dict([(seat['Direction'], seat.get('Player', '')) for seat in deal['Seats']])
    auctionHeader = '<tr>\n'
    for direction in globals.directions:
        auctionHeader += f'   <td align="direction in globals.directions:left" width="25%"><b>{direction}</b></td>\n'
    auctionHeader += '</tr>\n<tr>\n'
    for direction in globals.directions:
        auctionHeader += f'   <td align="left" width="25%"><i>{players[direction]}</i></td>\n'
    return auctionHeader + '</tr>\n'
    
    
def formatAuction(auction: List[str]) -> str:
    # take output of formatAuctionCalls and format it into html table rows
    # output: 
    # <tr>
    #    <td align="left" width="25%"> <br /></td>
    #    <td align="left" width="25%">1 ♣</td>
    #    <td align="left" width="25%">Pass</td>
    #    <td align="left" width="25%">2 ♣</td>
    # </tr>
    # <tr>
    #    <td align="left" width="25%">Pass</td>
    #    <td align="left" width="25%">2 ♠</td>
    #    <td align="left" width="25%">Pass</td>
    #    <td align="left" width="25%">3 NT</td>
    # </tr>
    # <tr>
    #    <td align="left" width="25%">Pass</td>
    #    <td align="left" width="25%">Pass</td>
    #    <td align="left" width="25%">Pass</td>
    #    <td align="left" width="25%"> <br /></td>
    # </tr>
    
    # extend auction to make length a multiple of four
    auction.extend([' '] * (4 - len(auction) % 4))
    
    # build rows
    newAuction = ''
    for i in range(len(auction)):
        if 0 == i % 4:
            newAuction += '<tr>\n'
        newAuction += f'   <td align="left" width="25%">{auction[i]}</td>\n'
        if 3 == i % 4:
            newAuction += '</tr>\n'
    return newAuction

def buildAuctionTable(deal: dict, width: int = 300) -> str:
    header = formatAuctionHeader(deal)
    auction = formatAuction((formatAuctionCalls(deal["Auction"], deal["Dealer"])))
    return f'<table align="center" border="0" cellpadding="0" cellspacing="0" style="width: {width}px;">\n<tbody>\n' + \
        header + \
        auction + \
        '</tbody></table>'
 
def buildHandTable(deal: dict, options: str) -> str:
    # build html to display deal
    # options is a string containing a letter for each hand to display (N, S, E, W) and 'A' if the auction is to be displayed
    hands = formatHandDiagrams(deal["Seats"])
    return '<div align="center"><table><tbody>\n' + \
            '   <tr>\n'  + \
            '      <td align="left" width="125"><br /></td>\n' + \
            '      <td align="left" width="125">' + (hands["North"] if 'N' in options else '') + '<br /></td>\n' + \
            '      <td align="left" width="125"><br /></td>\n' + \
            '   </tr>\n' + \
            '   <tr>\n'  + \
            '      <td align="left" width="125">' + (hands["West"] if 'W' in options else '') + '<br /></td>\n' + \
            '      <td align="left" width="125"><br /></td>\n' + \
            '      <td align="left" width="125">' + (hands["East"] if 'E' in options else '') + '<br /></td>\n' + \
            '   </tr>\n' + \
            '   <tr>\n'  + \
            '      <td align="left" width="125"><br /></td>\n' + \
            '      <td align="left" width="125">' + (hands["South"] if 'S' in options else '') + '<br /></td>\n' + \
            '      <td align="left" width="125"><br /></td>\n' + \
            '   </tr>\n' + \
            '</tbody></table></div>\n'
            
def buildSingleHand(hand: str) -> str:
    return f'<TABLE width="300" border="0" cellspacing="0" cellpadding="0" align="center"><TR><TD WIDTH="100%" Align="center">{hand}</TR></TABLE>'
        
    
def build(deal: dict, options: str) -> str:
    
    html = ''
    
    # rotate deal if necessary
    shiftNum = re.findall('[1-3]', options)
    if len(shiftNum) > 0:
        rotateDeal(deal, int(shiftNum[0]))
    
    # if a single seat is specified, format it as a single line
    seatsToShow = re.findall('[WNES]', options)
    if len(seatsToShow) == 1:
        for seat in deal['Seats']:
            if seat['Direction'] == globals.seats[seatsToShow[0]]:
                 html = buildSingleHand(formatHand(seat['Hand'], False))
                 break
    
    elif len(seatsToShow) > 1:
        html = buildHandTable(deal, options)
        
    # if specified, add auction
    if 'A' in options:
        html += buildAuctionTable(deal)
        
    return html

    

# for testing
if __name__ == '__main__' :
   
    sampleDeal = {"Seats": [{"Direction": "West", "Hand": {"Spades": "K6", "Hearts": "8643", "Diamonds": "Q954", "Clubs": "Q96"}}, {"Direction": "North"}, {"Direction": "East", "Hand": {"Spades": "AJT743", "Hearts": "", "Diamonds": "7", "Clubs": "AKJT84"}}, {"Direction": "South"}], "Auction": [""]}
    result = build(sampleDeal, 'EW')
    """
    sampleDeal = {'Dealer': 'West',
 'Seats': [{'Direction': 'West'},
  {'Direction': 'North', 
   'Hand': {'Spades': 'K7542',
    'Hearts': 'K752',
    'Diamonds': 'J6',
    'Clubs': 'Q4'}},
  {'Direction': 'East',
   'Hand': {'Spades': 'A6',
    'Hearts': 'AT6',
    'Diamonds': 'QT842',
    'Clubs': 'AT9'}},
  {'Direction': 'South'}],
 'Auction': ['P', 'P', '1D', '1S', 'D', '3S']}
    result = build(sampleDeal, 'NEA')
     """
    print (result)

 

