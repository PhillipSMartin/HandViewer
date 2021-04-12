# -*- coding: utf-8 -*-
"""
Created on Sat Apr 10 17:20:52 2021

@author: sarab
"""

def initialize():
    global suits
    global directions 
    suits = ["Spades", "Hearts", "Diamonds", "Clubs"]
    # West is first so it will appear first in the auction
    directions = ['West', 'North', 'East', 'South']
