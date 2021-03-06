import time
import pandas
from pandas import DataFrame
import matplotlib.pyplot as plt
import math

 


# Participant information below

typicalColumnName = 'Right Lower Leg z'
pathToFolder = '/Users/shana/Desktop/DesktopItems/BIOFEEDBACK/data/'

# Format of trials = participantKey : [rowValue, columnName, filePath, lastRow]
START_ROW_INDEX = 0
COLUMN_INDEX = 1
FILEPATH_INDEX = 2
LASTROW_INDEX = 3
trials = {
    # old end was 2769
    'p401' : [500, typicalColumnName, pathToFolder + 'Participant004-001.xlsx', 1528],
    # old end was 2769
    'p402' : [400, typicalColumnName, pathToFolder + 'Participant004-002.xlsx', 1429],
    'p1401' : [50, 'Right Lower Leg Angular Velocity (from radians)', pathToFolder + 'F014-001--Calculated_AV.xlsx', 1136],
    'p1402' : [150, 'Right Lower Leg Angular Velocity (from radians)', pathToFolder + 'F014-002--Calculated_AV.xlsx', 845],
    #old end was 3800
    'p2801' : [520, typicalColumnName, pathToFolder + 'Participant028-001.xlsx', 2108],
    #old end was 4000
    'p2802' : [700, typicalColumnName, pathToFolder + 'Participant028-002.xlsx', 2240],
    'p303' : [400, typicalColumnName, pathToFolder + 'Participant003-003.xlsx', 2600],
          }




# Input example: 'p401'
def setParticipant(participant):
    row = trials[participant][START_ROW_INDEX]
    columnName = trials[participant][COLUMN_INDEX]
    
    excel_foot_vel = None #Right foot y Angular Velocity
    footColumnName = None

    
    
    #Columns are indexed from zero
    if (participant != 'p1401' and participant != 'p1402') :
        excel_data_df = pandas.read_excel(trials[participant][FILEPATH_INDEX], sheet_name='Segment Angular Velocity', usecols=[51])
        excel_foot_vel = pandas.read_excel(trials[participant][FILEPATH_INDEX], sheet_name='Segment Angular Velocity', usecols=[53])
        footColumnName = 'Right Foot y'
        
    else:
        excel_data_df = pandas.read_excel(trials[participant][FILEPATH_INDEX], sheet_name='Segment Angular Velocity', usecols=[4])
    global inputLength
    inputLength = trials[participant][LASTROW_INDEX]
    
    return row, columnName, excel_data_df, excel_foot_vel, footColumnName, inputLength


# Convert data collection frequency to milliseconds
def convertMilliSecToRow(frequency, milliseconds):
    seconds = milliseconds / 1000
    return seconds * frequency








''' 

Version 1 of algorithm 

'''










'''
# Calculates gait events with Shank AV (MSW) and Foot AV (HS and TO)
# AV = Angular Velocity

# (1) MSW conditions: maxima, AV or prevAV > 100

# (2) HS conditions: if have foot AV, then if last MSW foot AV is positive, find foot AV max; 
# if last MSW foot AV is negative, then find foot AV min

# (3) TO conditions: wait 300ms after HS; same conditions as HS
'''
def getEventsWithShankAndFootAV(row, columnName, excel_data_df, excel_foot_vel, 
                                footColumnName, inputLength, waitRow80, waitRow300, frequency) :
    
    previousAngularVelocity = -1000.0
    previousDifference = -1000.0
    
    previousFootAV = -1000.0
    previousFootAVDifference = -1000.0
    
    MSW = 0
    HS = 0
    TO = 1
    startTime = 0
    
    data = { 'MSW': {'MSW Row': [], 'MSW Time' : [], 'MSW Angular Velocity' : []},
    'HS' : {'HS Row': [], 'HS Time' : [], 'HS Angular Velocity' : []},
    'TO' : {'TO Row': [], 'TO Time' : [], 'TO Angular Velocity' : []}
    }
    
    allexcel = { 'row' : [], 'value' : [] }
    
    # programStartTime = time.time()
    while (row < inputLength):
        
        row += 1
    
        angularVelocity = excel_data_df[columnName].iloc[row] * 180 / math.pi
        
        allexcel['row'].append(row)
        allexcel['value'].append(angularVelocity)
        
        if previousAngularVelocity == -1000 :
            previousAngularVelocity = angularVelocity
            continue
    
        elif previousDifference == -1000 :
            previousDifference = angularVelocity - previousAngularVelocity
            previousAngularVelocity = angularVelocity
            continue
        
        difference = angularVelocity - previousAngularVelocity
        
        
        # add condition for MSW != 0? 
        # article version: 
        # find max 
        if(previousDifference > 0 and difference < 0 and TO == 1) :
        # my version (for miscalculated ang vel): 
        # if(TO == 1) :
            # article version without prevAV > 100:
            if(angularVelocity > 100 or previousAngularVelocity > 100) :
            # my version:
            #if(angularVelocity < -150) :
            #if(angularVelocity > 100 or previousAngularVelocity > 100) :
            #if angularVelocity > 100 or previousAngularVelocity > 100 :
                data['MSW']['MSW Row'].append(row - 1)
                data['MSW']['MSW Time'].append((row - 1)*((1/frequency)))
                data['MSW']['MSW Angular Velocity'].append(previousAngularVelocity)
                
    
                # added this myself
                MSW = 1
                TO = 0
                previousAngularVelocity = angularVelocity
                previousDifference = difference
                continue
    
    
        footAV = 0
        footAVDifference = 0
    
        if excel_foot_vel is not None:
            
            footAV = excel_foot_vel[footColumnName].iloc[row] * 180 / math.pi
            
            if previousFootAV == -1000:
                previousFootAV = footAV
                previousAngularVelocity = angularVelocity
                previousDifference = difference
                continue
            
            elif previousFootAVDifference == -1000:
                previousFootAV = footAV
                previousFootAVDifference = footAV - previousFootAV
                previousAngularVelocity = angularVelocity
                previousDifference = difference
                continue
            
            footAVDifference = footAV - previousFootAV
            
    
        # finding HS with Foot AV
        if excel_foot_vel is not None and MSW == 1:
            
            MSWfootAV = excel_foot_vel[footColumnName].iloc[data['MSW']['MSW Row'][-1]] * 180 / math.pi
            
            # MSW has a negative foot angular velocity y
            if MSWfootAV < 0 :
            
                # find a maxima with positive foot AV
                if previousFootAVDifference > 0 and footAVDifference < 0 and footAV > 0:
                    data['HS']['HS Row'].append(row - 1)
                    data['HS']['HS Time'].append((row - 1)*(1/frequency))
                    data['HS']['HS Angular Velocity'].append(previousAngularVelocity)
                    
                    startTime = row
                    HS = 1
                    MSW = 0
                    
            else:
                
                # find a min and negative foot AV
                if previousFootAVDifference < 0 and footAVDifference > 0 and footAV < 0:
                    data['HS']['HS Row'].append(row - 1)
                    data['HS']['HS Time'].append((row - 1)*(1/frequency))
                    data['HS']['HS Angular Velocity'].append(previousAngularVelocity)
                    
                    startTime = row
                    HS = 1
                    MSW = 0
                    
                    
            previousFootAV = footAV
            previousFootAVDifference = footAVDifference
            previousAngularVelocity = angularVelocity
            previousDifference = difference
            continue
        
        
        # finding TO with Foot AV
        if excel_foot_vel is not None and HS == 1:
                
            MSWfootAV = excel_foot_vel[footColumnName].iloc[data['MSW']['MSW Row'][-1]] * 180 / math.pi
            currentTime = row - startTime
            
            # MSW has a negative foot angular velocity y
            if MSWfootAV < 0 and currentTime > waitRow300 :
            
                # find a maxima and positive foot AV
                if previousFootAVDifference > 0 and footAVDifference < 0 and footAV > 0:
                    data['TO']['TO Row'].append(row - 1)
                    data['TO']['TO Time'].append((row - 1)*(1/frequency))
                    data['TO']['TO Angular Velocity'].append(angularVelocity)
                    
                    TO = 1
                    HS = 0
                    
            elif currentTime > waitRow300 :
                
                # find a min and negative foot AV
                if previousFootAVDifference < 0 and footAVDifference > 0 and footAV < 0:
                    data['TO']['TO Row'].append(row - 1)
                    data['TO']['TO Time'].append((row - 1)*(1/frequency))
                    data['TO']['TO Angular Velocity'].append(angularVelocity)
                    
                    TO = 1
                    HS = 0
                   
            previousFootAV = footAV
            previousFootAVDifference = footAVDifference
            previousAngularVelocity = angularVelocity
            previousDifference = difference
            continue
                
    
        # finds a minima
        if previousDifference < 0 and difference > 0 and excel_foot_vel is None:
            
            # article version:
            if MSW == 1 and angularVelocity < 0 :
            # if MSW == 1 :
                minimaRow = row
                minima = angularVelocity
                # startTime = time.time() # time is in ns
                startCount = row
                # article: 100 hertz ; 80 ms
                # 60 hz = 60 frames/sec = 0.016666... sec/frame
                # 80 ms = 0.08 sec
                # 0.08/0.0166 = 4.8 = around 5 rows
                #while ( (time.time() * 1000) - (startTime * 1000) ) < 80 :
                #
                
                # this is the 80ms loop
                #
                # if ((time.time() * 1000) - (startTime * 1000)) <= 80 :
                #
                '''
                80 ms
                previous minima
                max closer to it
                then the next 'minima' is below the maxima & negative slope (so when it turns back to increasing)
                '''
                foundMinima = False
                while row - startCount < waitRow80 and not foundMinima:
                    
                    row += 1
                    
                    angularVelocity = excel_data_df[columnName].iloc[row] * 180 / math.pi
                    difference = angularVelocity - previousAngularVelocity
        
                    
                    # if a minima
                    if previousDifference < 0 and difference > 0 :
                        minimaRow = row
                        minima = angularVelocity
                    
                    # if any maxima in 80 ms window and magnitude diff <= 10
                    if previousDifference > 0 and difference < 0 and angularVelocity - minima <= 10 :
                        # Code add here: immediate minima = HS
    
    
                        #
                        #while ( excel_data_df['Right Lower Leg z'].iloc[row]  * (180/math.pi) )< possibleMaxima and time <= 80 :
                        #
                        # search for immediate minima, previous diff is negative and diff is positive
                        maxima = angularVelocity
                        while not foundMinima and row - startCount < waitRow80 :
                            # wait for next input = increase row
                            
                            previousAngularVelocity = angularVelocity
                            previousDifference = difference
                            
                            row += 1
                            angularVelocity = excel_data_df[columnName].iloc[row] * 180 / math.pi
                            difference = angularVelocity - previousAngularVelocity
                            
                            if previousDifference < 0 and difference > 0 :
                                minimaRow = row
                                minima = angularVelocity
                                foundMinima = True
    
                    
                    previousAngularVelocity = angularVelocity
                    previousDifference = difference
    
                #
                # 80 ms interval ended
                #
                
                # Code add here: previous angular velocity = HS
                # aka for my code: minima = HS
                data['HS']['HS Row'].append(minimaRow)
                data['HS']['HS Time'].append(minimaRow*(1/frequency))
                data['HS']['HS Angular Velocity'].append(minima)
    
                MSW = 0
    
                #added this myself
                HS = 1
                #
                #startTime = time.time() # time is in ns
                #
                startTime = row
                previousAngularVelocity = angularVelocity
                previousDifference = difference
                continue
        
            else:
                #
                #currentTimeMiliSec = (time.time() * 1000) - (startTime * 1000)
                #
                currentTime = row - startTime
                #
                #if HS == 1 and angularVelocity < -20 and currentTimeMiliSec > 300 :
                #
                # 300 ms = 0.3 sec
                # 0.3/0.01666 = 18.07
                # 
                # article version has AV < -20 while I used -50:
                if HS == 1 and angularVelocity < -50 and currentTime > waitRow300 :
                # my version:
                #if HS == 1 and previousAngularVelocity > 0 and angularVelocity < 0 and currentTime > 18:
                    HS = 0
                    TO = 1
                    # add here: previousAngularVelocity = TO
                    data['TO']['TO Row'].append(row-1)
                    data['TO']['TO Time'].append((row-1)*((1/frequency)))
                    data['TO']['TO Angular Velocity'].append(previousAngularVelocity)
    
                    previousAngularVelocity = angularVelocity
                    previousDifference = difference
                    continue
                
            
                
        previousAngularVelocity = angularVelocity
        previousDifference = difference
        
    return data, allexcel











''' 

Version 2 of algorithm 

'''










'''
# Calculates gait events with Shank AV (MSW) and Foot AV (HS and TO)
# AV = Angular Velocity
# PROBLEM: MSW only checks for one direction, so when person turns around (and footAV Y changes), then it won't be detected

# (1) MSW conditions: maxima, AV or prevAV > 100

# (2) HS conditions: if have foot AV, then if last MSW foot AV is positive, find foot AV max; 
# if last MSW foot AV is negative, then find foot AV min

# (3) TO conditions: wait 300ms after HS; same conditions as HS
'''
def getEventsWithFootAV(row, columnName, excel_data_df, excel_foot_vel, 
                                footColumnName, inputLength, waitRow80, waitRow300, frequency) :
    
    previousAngularVelocity = -1000.0
    previousDifference = -1000.0
    
    previousFootAV = -1000.0
    previousFootAVDifference = -1000.0
    
    MSW = 0
    HS = 0
    TO = 1
    startTime = 0
    
    data = { 'MSW': {'MSW Row': [], 'MSW Time' : [], 'MSW Angular Velocity' : []},
    'HS' : {'HS Row': [], 'HS Time' : [], 'HS Angular Velocity' : []},
    'TO' : {'TO Row': [], 'TO Time' : [], 'TO Angular Velocity' : []}
    }
    
    allexcel = { 'row' : [], 'value' : [] }
    
    # programStartTime = time.time()
    while (row < inputLength):
        
        row += 1
    
        angularVelocity = excel_data_df[columnName].iloc[row] * 180 / math.pi
        
        allexcel['row'].append(row)
        allexcel['value'].append(angularVelocity)
        
        if previousAngularVelocity == -1000 :
            previousAngularVelocity = angularVelocity
            continue
    
        elif previousDifference == -1000 :
            previousDifference = angularVelocity - previousAngularVelocity
            previousAngularVelocity = angularVelocity
            continue
        
        difference = angularVelocity - previousAngularVelocity
        
        
        ''' Start foot AV setup section '''
        
        footAV = 0
        footAVDifference = 0
    
        if excel_foot_vel is not None:
            
            footAV = excel_foot_vel[footColumnName].iloc[row] * 180 / math.pi
            
            if previousFootAV == -1000:
                previousFootAV = footAV
                previousAngularVelocity = angularVelocity
                previousDifference = difference
                continue
            
            elif previousFootAVDifference == -1000:
                previousFootAV = footAV
                previousFootAVDifference = footAV - previousFootAV
                previousAngularVelocity = angularVelocity
                previousDifference = difference
                continue
            
            footAVDifference = footAV - previousFootAV
            
        ''' End foot AV setup section '''
        
        
        # add condition for MSW != 0? 
        # article version: 
        # find min
        if(previousFootAVDifference < 0 and footAVDifference > 0 and TO == 1) :
            print("\nRow = ", row, "\nfoot AV y = ", footAV, "\nShank AV = ", angularVelocity)
        # my version (for miscalculated ang vel): 
        # if(TO == 1) :
            # article version without prevAV > 100:
            if(angularVelocity > 0) :
            # my version:
            #if(angularVelocity < -150) :
            #if(angularVelocity > 100 or previousAngularVelocity > 100) :
            #if angularVelocity > 100 or previousAngularVelocity > 100 :
                data['MSW']['MSW Row'].append(row - 1)
                data['MSW']['MSW Time'].append((row - 1)*((1/frequency)))
                data['MSW']['MSW Angular Velocity'].append(previousAngularVelocity)
                
    
                # added this myself
                MSW = 1
                TO = 0
                previousFootAV = footAV
                previousFootAVDifference = footAVDifference
                previousAngularVelocity = angularVelocity
                previousDifference = difference
                continue
    
            
    
        # finding HS with Foot AV
        if MSW == 1:
            
            MSWfootAV = excel_foot_vel[footColumnName].iloc[data['MSW']['MSW Row'][-1]] * 180 / math.pi
            
            # MSW has a negative foot angular velocity y
            if MSWfootAV < 0 :
            
                # find a maxima with positive foot AV
                if previousFootAVDifference > 0 and footAVDifference < 0 and footAV > 0:
                    data['HS']['HS Row'].append(row - 1)
                    data['HS']['HS Time'].append((row - 1)*(1/frequency))
                    data['HS']['HS Angular Velocity'].append(previousAngularVelocity)
                    
                    startTime = row
                    HS = 1
                    MSW = 0
                    
            else:
                
                # find a min and negative foot AV
                if previousFootAVDifference < 0 and footAVDifference > 0 and footAV < 0:
                    data['HS']['HS Row'].append(row - 1)
                    data['HS']['HS Time'].append((row - 1)*(1/frequency))
                    data['HS']['HS Angular Velocity'].append(previousAngularVelocity)
                    
                    startTime = row
                    HS = 1
                    MSW = 0
                    
                    
            previousFootAV = footAV
            previousFootAVDifference = footAVDifference
            previousAngularVelocity = angularVelocity
            previousDifference = difference
            continue
        
        
        # finding TO with Foot AV
        if HS == 1:
                
            MSWfootAV = excel_foot_vel[footColumnName].iloc[data['MSW']['MSW Row'][-1]] * 180 / math.pi
            currentTime = row - startTime
            
            # MSW has a negative foot angular velocity y
            if MSWfootAV < 0 and currentTime > waitRow300 :
            
                # find a maxima and positive foot AV
                if previousFootAVDifference > 0 and footAVDifference < 0 and footAV > 0:
                    data['TO']['TO Row'].append(row - 1)
                    data['TO']['TO Time'].append((row - 1)*(1/frequency))
                    data['TO']['TO Angular Velocity'].append(angularVelocity)
                    
                    TO = 1
                    HS = 0
                    
            elif currentTime > waitRow300 :
                
                # find a min and negative foot AV
                if previousFootAVDifference < 0 and footAVDifference > 0 and footAV < 0:
                    data['TO']['TO Row'].append(row - 1)
                    data['TO']['TO Time'].append((row - 1)*(1/frequency))
                    data['TO']['TO Angular Velocity'].append(angularVelocity)
                    
                    TO = 1
                    HS = 0
                   
            previousFootAV = footAV
            previousFootAVDifference = footAVDifference
            previousAngularVelocity = angularVelocity
            previousDifference = difference
            continue
                
                
            
        previousFootAV = footAV
        previousFootAVDifference = footAVDifference
        previousAngularVelocity = angularVelocity
        previousDifference = difference
        
    return data, allexcel








'''

Version 3 of algorithm


'''








'''
Calculates gait events with Shank AV (MSW) and Foot AV (HS and TO)
AV = Angular Velocity
PROBLEM: MSW only checks for one direction, so when person turns around (and footAV Y changes), then it won't be detected

(1) MSW conditions: foot AV y minima and negative and shank angular acceleration < 0 within 3 rows [+ ADD OR WILL BE < IN A BIT?]

(2) HS conditions: if last MSW foot AV is positive, find foot AV max; 
if last MSW foot AV is negative, then find foot AV min

(3) TO conditions: wait 300ms after HS; same conditions as HS except foot AV max needs to be > 1 and foot AV min needs
to be < -1
'''
def getEventsWithFootAVShankAngVel(row, columnName, excel_data_df, excel_foot_vel, 
                               footColumnName, inputLength, waitRow80, waitRow300, frequency) :
    
    previousAngularVelocity = -1000.0
    previousDifference = -1000.0
    
    previousFootAV = -1000.0
    previousFootAVDifference = -1000.0
    
    MSW = 0
    HS = 0
    TO = 1
    startTime = 0
    
    data = { 'MSW': {'MSW Row': [], 'MSW Time' : [], 'MSW Angular Velocity' : []},
    'HS' : {'HS Row': [], 'HS Time' : [], 'HS Angular Velocity' : []},
    'TO' : {'TO Row': [], 'TO Time' : [], 'TO Angular Velocity' : []}
    }
    
    allexcel = { 'row' : [], 'value' : [] }
    
    # programStartTime = time.time()
    while (row < inputLength):
        
        row += 1
    
        angularVelocity = excel_data_df[columnName].iloc[row] * 180 / math.pi
        
        allexcel['row'].append(row)
        allexcel['value'].append(angularVelocity)
        
        if previousAngularVelocity == -1000 :
            previousAngularVelocity = angularVelocity
            continue
    
        elif previousDifference == -1000 :
            previousDifference = angularVelocity - previousAngularVelocity
            previousAngularVelocity = angularVelocity
            continue
        
        difference = angularVelocity - previousAngularVelocity
        
        
        ''' Start foot AV setup section '''
        
        footAV = 0
        footAVDifference = 0
    
        if excel_foot_vel is not None:
            
            footAV = excel_foot_vel[footColumnName].iloc[row]
            
            if previousFootAV == -1000:
                previousFootAV = footAV
                previousAngularVelocity = angularVelocity
                previousDifference = difference
                continue
            
            elif previousFootAVDifference == -1000:
                previousFootAV = footAV
                previousFootAVDifference = footAV - previousFootAV
                previousAngularVelocity = angularVelocity
                previousDifference = difference
                continue
            
            footAVDifference = footAV - previousFootAV
            
        ''' End foot AV setup section '''
        
        
        # add condition for MSW != 0? 
        # article version: 
        # find min
        if(previousFootAVDifference < 0 and footAVDifference > 0 and footAV < 0 and TO == 1) :
            
        # my version (for miscalculated ang vel): 
        # if(TO == 1) :
            # article version without prevAV > 100:
            if(angularVelocity > 0) :
            # my version:
            #if(angularVelocity < -150) :
            #if(angularVelocity > 100 or previousAngularVelocity > 100) :
            #if angularVelocity > 100 or previousAngularVelocity > 100 :
                data['MSW']['MSW Row'].append(row - 1)
                data['MSW']['MSW Time'].append((row - 1)*((1/frequency)))
                data['MSW']['MSW Angular Velocity'].append(previousAngularVelocity)
                
    
                # added this myself
                MSW = 1
                TO = 0
                previousFootAV = footAV
                previousFootAVDifference = footAVDifference
                previousAngularVelocity = angularVelocity
                previousDifference = difference
                continue
        
            else :
                count = 0
                while (count < 3) :
                    row += 1
                    angularVelocity = excel_data_df[columnName].iloc[row] * 180 / math.pi
                    if (angularVelocity > 0) :
                        data['MSW']['MSW Row'].append(row - 1)
                        data['MSW']['MSW Time'].append((row - 1)*((1/frequency)))
                        data['MSW']['MSW Angular Velocity'].append(previousAngularVelocity)
                        
            
                        # added this myself
                        MSW = 1
                        TO = 0
                        previousFootAV = footAV
                        previousFootAVDifference = footAVDifference
                        previousAngularVelocity = angularVelocity
                        previousDifference = difference
                        count = 3
                    count += 1
                continue
    
            
    
        # finding HS with Foot AV
        if MSW == 1:
            
            MSWfootAV = excel_foot_vel[footColumnName].iloc[data['MSW']['MSW Row'][-1]]
            
            # MSW has a negative foot angular velocity y
            if MSWfootAV < 0 :
            
                # find a maxima with positive foot AV
                if previousFootAVDifference > 0 and footAVDifference < 0 and footAV > 0:
                    data['HS']['HS Row'].append(row - 1)
                    data['HS']['HS Time'].append((row - 1)*(1/frequency))
                    data['HS']['HS Angular Velocity'].append(previousAngularVelocity)
                    
                    startTime = row
                    HS = 1
                    MSW = 0
                    
            else:
                
                # find a min and negative foot AV
                if previousFootAVDifference < 0 and footAVDifference > 0 and footAV < 0:
                    data['HS']['HS Row'].append(row - 1)
                    data['HS']['HS Time'].append((row - 1)*(1/frequency))
                    data['HS']['HS Angular Velocity'].append(previousAngularVelocity)
                    
                    startTime = row
                    HS = 1
                    MSW = 0
                    
                    
            previousFootAV = footAV
            previousFootAVDifference = footAVDifference
            previousAngularVelocity = angularVelocity
            previousDifference = difference
            continue
        
        
        # finding TO with Foot AV
        if HS == 1:
                
            MSWfootAV = excel_foot_vel[footColumnName].iloc[data['MSW']['MSW Row'][-1]] 
            currentTime = row - startTime
            
            
            # MSW has a negative foot angular velocity y
            if MSWfootAV < 0 and currentTime > waitRow300 :
            
                # find a maxima and positive foot AV
                if previousFootAVDifference > 0 and footAVDifference < 0 and footAV > 1:
                    data['TO']['TO Row'].append(row - 1)
                    data['TO']['TO Time'].append((row - 1)*(1/frequency))
                    data['TO']['TO Angular Velocity'].append(angularVelocity)
                    
                    print("Row = ", row, " Foot AV y = ", footAV)
                    
                    TO = 1
                    HS = 0
                    
            elif currentTime > waitRow300 :
                
                # find a min and negative foot AV
                if previousFootAVDifference < 0 and footAVDifference > 0 and footAV < -1:
                    data['TO']['TO Row'].append(row - 1)
                    data['TO']['TO Time'].append((row - 1)*(1/frequency))
                    data['TO']['TO Angular Velocity'].append(angularVelocity)
                    
                    print("Row = ", row, " Foot AV y = ", footAV)
                    
                    TO = 1
                    HS = 0
                   
            previousFootAV = footAV
            previousFootAVDifference = footAVDifference
            previousAngularVelocity = angularVelocity
            previousDifference = difference
            continue
                
                
            
        previousFootAV = footAV
        previousFootAVDifference = footAVDifference
        previousAngularVelocity = angularVelocity
        previousDifference = difference
        
    return data, allexcel
    
    
    
    
    
    
    
    
    
    
    

# Frequency at which data is taken:
# Participant 4 = 60 Hz
# Participant 14 = 60 Hz
# Participant 28 = 100Hz
# Participant 3 = 60 Hz


def main(participantName, frequency, title):
    
    participant = setParticipant(participantName)
    waitRow80 = convertMilliSecToRow(frequency, 80)
    waitRow300 = convertMilliSecToRow(frequency, 300)
    
    '''
    gaitEvents = getEventsWithFootAV(participant[0], participant[1], participant[2], 
                                             participant[3], participant[4], participant[5], 
                                             waitRow80, waitRow300, frequency)
    '''
    
    gaitEvents = getEventsWithFootAVShankAngVel(participant[0], participant[1], participant[2], 
                                             participant[3], participant[4], participant[5], 
                                             waitRow80, waitRow300, frequency)
    
    MSWdf = DataFrame(gaitEvents[0]['MSW'],columns=['MSW Row', 'MSW Time', 'MSW Angular Velocity'])
    print (MSWdf)
    # MSWdf.plot(x ='MSW Time', y='MSW Angular Velocity', kind = 'scatter')
    # plt.show()
    
    HSdf = DataFrame(gaitEvents[0]['HS'],columns=[ 'HS Row', 'HS Time', 'HS Angular Velocity'])
    print (HSdf)
    # HSdf.plot(x ='HS Time', y='HS Angular Velocity', kind = 'scatter')
    # plt.show()
    
    TOdf = DataFrame(gaitEvents[0]['TO'],columns=[ 'TO Row', 'TO Time', 'TO Angular Velocity'])
    print (TOdf)
    # TOdf.plot(x ='TO Time', y='TO Angular Velocity', kind = 'scatter')
    # plt.show()
    
    
    fig=plt.figure()
    ax=fig.add_axes([0,0,1,1])
    # ax.scatter(allexcel['row'], allexcel['value'], color='r')
    ax.scatter(gaitEvents[0]['MSW'][ 'MSW Time'], gaitEvents[0]['MSW']['MSW Angular Velocity'], color='r')
    ax.scatter(gaitEvents[0]['HS'][ 'HS Time'], gaitEvents[0]['HS']['HS Angular Velocity'], color='b')
    ax.scatter(gaitEvents[0]['TO'][ 'TO Time'], gaitEvents[0]['TO']['TO Angular Velocity'], color='g')
    
    ax.set_xlabel('Time')
    ax.set_ylabel('AngularVelocity')
    #ax.set_title('14-02 (actual data): MSW  < -150 + HS difference is > 0 + TO is < 0 while prev > 0')
    ax.set_title(participantName + title)
    plt.show()
    








if __name__ == "__main__":
    
    #print("60 hz to 300ms = ", convertMilliSecToRow(60, 300), "100 hz to 300ms = ", convertMilliSecToRow(100, 300))
    
    print('PARTICIPANT 4-01\n')
    main('p401', 60, ': #2; MSW uses footAV Y < 0 + footAV Y min w/ shank AV > 0 within 3 rows')
    
    print('PARTICIPANT 4-02\n')
    main('p402', 60, ': #2; MSW uses footAV Y < 0 + footAV Y min w/ shank AV > 0 within 3 rows')
    
    print('PARTICIPANT 28-01\n')
    main('p2801', 100, ': #2; MSW uses footAV Y < 0 + footAV Y min w/ shank AV > 0 within 3 rows')
    
    print('PARTICIPANT 28-02\n')
    main('p2802', 100, ': #2; MSW uses footAV Y < 0 + footAV Y min w/ shank AV > 0 within 3 rows + TO > -1')
    
    '''
    ^ CHECK (1) PARTICIPANT NAME, 
            (2) FREQUENCY, 
            (3) TITLE ABOVE
    '''


        
