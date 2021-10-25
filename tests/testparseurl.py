# -*- coding: utf-8 -*-
"""
Created on Sat Apr 10 11:33:59 2021

@author: sarab
"""
import parseurl
import sys

def main(url: str):
    # build a dictionary from the specfied url and print it
    print(parseurl.main(url))
    
main(sys.argv[1])