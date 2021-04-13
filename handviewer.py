# -*- coding: utf-8 -*-
"""
Created on Sat Apr 10 11:33:59 2021

@author: sarab
"""
import parseurl
import buildhtml
import sys

def main(url: str, options: str, outputfile: str):
# url is the url of a BBO handviewer deal
# options is a string containing one or more of 'NSEWA' and a number 
#   NSEW specify the seats to print, A specifies to print the auction, the number indicates how many seats to shift the deal (clockwise) 
    
    # build the html
    html = buildhtml.build(parseurl.parse(url), options)
   
    # write it to the specified file
    f = open(outputfile, 'w')
    f.write(html)
    f.close()
    
    print(f"Html has been written to {outputfile}")
    
    
main(*sys.argv[1:])