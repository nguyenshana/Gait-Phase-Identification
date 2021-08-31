#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun May  2 15:32:38 2021

@author: shana
"""
import pandas


def main(participantName, rows):
    # Participant information below
    pathToFolder = '/Users/shana/Desktop/DesktopItems/BIOFEEDBACK/data/'
    
    FORWARD_START_ROW = 0
    FORWARD_END_ROW = 1
    BACKWARD_START_ROW = 2
    BACKWARD_END_ROW = 3
    FILEPATH_INDEX = 4
    trials = {
            'p401' : [500, 1528, 1594, 2695, pathToFolder + 'Participant004-001.xlsx'], 
            'p402' : [400, 1429, 1513, 2446, pathToFolder + 'Participant004-002.xlsx'],
             #turnaround point is unknown
            'p1401' : [50, -1, -1, 1136, 'Right Lower Leg Angular Velocity (from radians)', pathToFolder + 'F014-001--Calculated_AV.xlsx'],
             #turnaround point is unknown
            'p1402' : [150, -1, -1, 845, 'Right Lower Leg Angular Velocity (from radians)', pathToFolder + 'F014-002--Calculated_AV.xlsx'],
            'p2801' : [520, 2108, 2209, 3800, pathToFolder + 'Participant028-001.xlsx'],
            'p2802' : [700, 2240, 2362, 4000, pathToFolder + 'Participant028-002.xlsx'],
            'p303' : [400, 1500, 1588, 2638, pathToFolder + 'Participant003-003.xlsx'],
            'p3103' : [490, 3648, 3845, 7186, pathToFolder + 'Participant031-003.xlsx'], 
              }
    
    # XSENS EXCEL FILES SETUP
 
    excel_shank_AccelZ = pandas.read_excel(trials[participantName][FILEPATH_INDEX], sheet_name='Segment Acceleration', usecols=[51])
    
    print("got shank acceleration Z quat columns")
    
    row = trials[participantName][FORWARD_START_ROW]
    lastRow = trials[participantName][BACKWARD_END_ROW]
    
    while row < lastRow:
        
        if row in rows:
            print( excel_shank_AccelZ['Right Lower Leg z'].iloc[row] )
    
        row += 1
        
        
        

if __name__ == "__main__":
    
    
    row = [578,647,714,783,849,917,985,1053,1121,1189,1257,
1328,1615,1688,1757,1826,1897,1966,2035,2106,2177,2245,2313,2377,2444,2511,2579,2647]
    
    print('\nPARTICIPANT 4-01\n')
    main('p401', row)
    
    row = [434,504,571,638,707,773,842,911,977,1047,1114,1183,1537,1604,1670,1735,1800,1865,1930,1996,
2059,2123,2189,2253,2318,2384]

    print('\nPARTICIPANT 4-02\n')
    main('p402', row)
    
    row = [607,737,869,996,1124,1249,1374,1501,1627,1753,1884,2016,2255,2374,2505,2628,2752,2874,2995,
3117,3240,3361,3486,3612,3747]
    
    print('\nPARTICIPANT 28-01\n')
    main('p2801', row)
    
    row = [772,902,1022,1148,1272,1397,1524,1647,1773,1896,2023,2151,2401,2523,2644,2768,2888,
3010,3132,3254,3377,3500,3622,3747,3885]
    
    print('\nPARTICIPANT 28-02\n')
    main('p2802', row)
    
    row = [482,558,621,710,774,843,916,991,1137,1615,1693,1763,1836,1910,1984,2058,2129,2199,2271,
2343,2415,2487,2560,2636]
    
    print('\nPARTICIPANT 3-03\n')
    main('p303', row)
    
    row = [564,746,893,1049,1234,1418,1568,1643,3944,4122,4312,4501,4679,4864,5044,5222,5426,
5621,5814,6005,6181,6351,6509,664,6840,7010,7165]
    
    print('\nPARTICIPANT 31-03\n')
    main('p3103', row)
    
    
    