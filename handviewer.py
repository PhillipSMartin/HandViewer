# -*- coding: utf-8 -*-
"""
Created on Sat Apr 10 11:33:59 2021

@author: sarab

Git commands:
    git add .
    git status
    git commit -m "some comment"
    git push -u  origin main
"""
import parseurl
import buildhtml
import inputdeal
import sys
import re
import json

def main(input: str, options: str, outputfile: str):
# input is either
#    the url of a BBO handviewer deal
#    * to indicate console entry
#    ** to indicate deal was previously saved in a json file with the same name as the outputfile specification
# options is a string containing one or more of 'NSEWA' and a number 
#   NSEW specify the seats to print, A specifies to print the auction, the number indicates how many seats to shift the deal (clockwise) 
# output file should be previx only - both json and html files will be created

    assert '.' not in outputfile, "Output file name should be prefix only" 
    
    deal = {}
    
    # build deal
    if input == '**':
        saveFile = open(outputfile + ".json", "r")
        deal = json.load(saveFile)
        saveFile.close()
    else:
        saveFile = open(outputfile + ".json", "w")
        if input == '*':
            deal = inputdeal.inputDeal()
            json.dump(deal, saveFile)
        elif re.match("http", input):
            deal = parseurl.parse(input)
            json.dump(deal, saveFile)
        saveFile.close()
     
    assert deal, 'Input must be *, **, or start with http'
    
    # build the html
    html = buildhtml.build(deal, options)
   
    # write it to the specified file
    f = open(outputfile + ".html", 'w')
    f.write(html)
    f.close()
    
    print(f"Html has been written to {outputfile}")
    
    
main(*sys.argv[1:])