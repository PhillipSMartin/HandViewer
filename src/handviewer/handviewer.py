# -*- coding: utf-8 -*-
"""
Created on Sat Apr 10 11:33:59 2021

@author: sarab


"""
import argparse
import buildhtml
import inputdeal
import json
import parseurl
import re


class HandViewer:
    def __init__(self):
        parser = argparse.ArgumentParser(description = 'Handviewer Tool', )
        parser.add_argument('input', help='html string, * for console input, or ** for previous deal ')
        parser.add_argument('-n', '--north', action='store_true', help='print North hand')
        parser.add_argument('-e', '--east', action='store_true', help='print East hand')
        parser.add_argument('-s', '--south', action='store_true', help='print South hand')
        parser.add_argument('-w', '--west', action='store_true', help='print West hand')
        parser.add_argument('-a', '--auction', action='store_true', help='print auction')
        parser.add_argument('-r', '--rotate', type=int, help='number of seats to rotate clockwise')
        parser.add_argument('-o', '--output', default='output', help='common prefix for json and html output files')
        self._args = parser.parse_args()
    
    def __call__(self):
        assert '.' not in self._args.output, "Output file name should be prefix only" 
        
        deal = {}
        
        # build deal
        if self._args.input == '**':
            saveFile = open(self._args.output + ".json", "r")
            deal = json.load(saveFile)
            saveFile.close()
        else:
            saveFile = open(self._args.output + ".json", "w")
            if self._args.input == '*':
                deal = inputdeal.inputDeal()
                json.dump(deal, saveFile)
            elif re.match("http", self._args.input):
                deal = parseurl.parse(self._args.input)
                json.dump(deal, saveFile)
            saveFile.close()
         
        assert deal, 'Input must be *, **, or start with http'
        
        # build the html
        html = buildhtml.build(deal, self._args)
       
        # write it to the specified file
        f = open(self._args.output + ".html", 'w')
        f.write(html)
        f.close()
        
        print(f"Html has been written to {self._args.output}")
    
if __name__ == '__main__':
    hv = HandViewer()
    hv()
