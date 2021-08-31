#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Aug  1 11:24:53 2021

@author: shana
"""
import csv
import scipy.signal as sc
import numpy as np


def crossCorrelate():
    
    # longer fiile
    csv_angAccelX_1a = list(csv.DictReader(open('/Users/shana/Downloads/Test 1a.csv', mode='r')) )
    # shorter file
    csv_angAccelX_1b = list(csv.DictReader(open('/Users/shana/Downloads/Test 1b.csv', mode='r')) )

    timeName = '\ufefftime_s' #\ufefftime_s
    aValName = 'a'
    bValName = 'b'
    
    aTime = []
    bTime = []
    aVal = []
    bVal = []
    
    row = 0
    
    # getting all data
    while row < 3368:
        
        if row >= 3326:
            bTime.append( 0 )
            bVal.append( 0 )
        else:
            bTime.append(float( csv_angAccelX_1b[row][timeName] ) )
            bVal.append(float( csv_angAccelX_1b[row][bValName] ) )
            
        aTime.append(float( csv_angAccelX_1a[row][timeName] ) ) 
        aVal.append(float( csv_angAccelX_1a[row][aValName] ) )
        
        row += 1
        
        
    '''   
    TRYING 2D
    
    [[time, value],
     [time, value]]
    '''
    
    a2d = []
    b2d = []
    
    for i in range(len(aTime)):
        a2d.append([aTime[i], aVal[i]])
        
    for i in range(len(bTime)):
        b2d.append([bTime[i], bVal[i]])
        
        
    print("2D CORRELATION = ", sc.correlate2d( a2d, b2d ))
    

    '''   
    TRYING 1D
    
    
    # 1D cross correlation
    print("1D CORRELATION = ", sc.correlate( aVal, bVal ))
    '''
    
    


if __name__ == "__main__":
    
    crossCorrelate()