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
import argparse
import buildhtml
import inputdeal
import json
import parseurl
import re


def main(args):
    assert '.' not in args.output, "Output file name should be prefix only" 
    
    deal = {}
    
    # build deal
    if args.input == '**':
        saveFile = open(args.output + ".json", "r")
        deal = json.load(saveFile)
        saveFile.close()
    else:
        saveFile = open(args.output + ".json", "w")
        if args.input == '*':
            deal = inputdeal.inputDeal()
            json.dump(deal, saveFile)
        elif re.match("http", args.input):
            deal = parseurl.parse(args.input)
            json.dump(deal, saveFile)
        saveFile.close()
     
    assert deal, 'Input must be *, **, or start with http'
    
    # build the html
    html = buildhtml.build(deal, args)
   
    # write it to the specified file
    f = open(args.output + ".html", 'w')
    f.write(html)
    f.close()
    
    print(f"Html has been written to {args.output}")
    
    
if __name__ == '__main__':
    parser = argparse.ArgumentParser(description = 'Handviewer Tool', )
    parser.add_argument('input', help='html string, * for console input, or ** for previous deal ')
    parser.add_argument('-n', '--north', action='store_true', help='print North hand')
    parser.add_argument('-e', '--east', action='store_true', help='print East hand')
    parser.add_argument('-s', '--south', action='store_true', help='print South hand')
    parser.add_argument('-w', '--west', action='store_true', help='print West hand')
    parser.add_argument('-a', '--auction', action='store_true', help='print auction')
    parser.add_argument('-r', '--rotate', type=int, help='number of seats to rotate clockwise')
    parser.add_argument('-o', '--output', default='output', help='common prefix for json and html output files')
    
    main(parser.parse_args())
