# -*- coding: utf-8 -*-
import time
import pandas
from pandas import DataFrame
import matplotlib.pyplot as plt
import math



# Participant information below

shankAVzColumnName = 'Right Lower Leg z'
pathToFolder = '/Users/shana/Desktop/DesktopItems/BIOFEEDBACK/data/'

# Format of trials = participantKey : [rowValue, columnName, filePath, lastRow]
FORWARD_START_ROW = 0
FORWARD_END_ROW = 1
BACKWARD_START_ROW = 2
BACKWARD_END_ROW = 3
SHANK_AVZ_COLUMN_INDEX = 4
FILEPATH_INDEX = 5
trials = {
        'p401' : [500, 1528, 1594, 2695, shankAVzColumnName, pathToFolder + 'Participant004-001.xlsx'], #end 2695
        'p402' : [400, 1429, 1513, 2446, shankAVzColumnName, pathToFolder + 'Participant004-002.xlsx'],
        # turnaround point is unknown
        'p1401' : [50, -1, -1, 1136, 'Right Lower Leg Angular Velocity (from radians)', pathToFolder + 'F014-001--Calculated_AV.xlsx'],
        # turnaround point is unknown
        'p1402' : [150, -1, -1, 845, 'Right Lower Leg Angular Velocity (from radians)', pathToFolder + 'F014-002--Calculated_AV.xlsx'],
        'p2801' : [520, 2108, 2209, 3800, shankAVzColumnName, pathToFolder + 'Participant028-001.xlsx'],
        'p2802' : [700, 2240, 2362, 4000, shankAVzColumnName, pathToFolder + 'Participant028-002.xlsx'],
        'p303' : [400, 1500, 1588, 2638, shankAVzColumnName, pathToFolder + 'Participant003-003.xlsx'],
        'p3103' : [490, 3648, 3845, 7186, shankAVzColumnName, pathToFolder + 'Participant031-003.xlsx'], #start at 3845
          }




# Input example: 'p401'
def setParticipant(participant):
    forwardStartRow = trials[participant][FORWARD_START_ROW]
    forwardEndRow = trials[participant][FORWARD_END_ROW]
    backwardStartRow = trials[participant][BACKWARD_START_ROW]
    backwardEndRow = trials[participant][BACKWARD_END_ROW]
    
    shankAVzColumnName = trials[participant][SHANK_AVZ_COLUMN_INDEX]
    excel_foot_AVy = None #Right foot y Angular Velocity
    footAVyColumnName = None
    
    #Columns are indexed from zero
    if (participant != 'p1401' and participant != 'p1402') :
        excel_shank_AVz = pandas.read_excel(trials[participant][FILEPATH_INDEX], sheet_name='Segment Angular Velocity', usecols=[51])
        excel_foot_AVy = pandas.read_excel(trials[participant][FILEPATH_INDEX], sheet_name='Segment Angular Velocity', usecols=[53])
        footAVyColumnName = 'Right Foot y'
    # Participant 14 uses the calculated AV
    else:
        excel_shank_AVz = pandas.read_excel(trials[participant][FILEPATH_INDEX], sheet_name='Segment Angular Velocity', usecols=[4])
    
    return forwardStartRow, forwardEndRow, backwardStartRow, backwardEndRow, shankAVzColumnName, footAVyColumnName, excel_shank_AVz, excel_foot_AVy



# Convert data collection frequency to milliseconds
def convertMilliSecToRow(frequency, milliseconds):
    seconds = milliseconds / 1000
    return seconds * frequency




'''
Calculates gait events with Shank AV (MSW) and Foot AV (HS and TO)
AV = Angular Velocity
NOTES: 
    - indicate 'forward' or 'backward' in the direction (backward will multiply footAVy by -1)
    - MSW 50ms is arbitrary (wanted to check 3 extra rows)
    - ALL EVENTS CURRENTLY ADD THE ROW BEFORE, so not exactly 'real time'

(1) MSW conditions: foot AV y minima and negative and shank angular velocity > 0 within 50ms

(2) HS conditions: find positive foot AV max

(3) TO conditions: wait 300ms after HS; find foot AV max that is > 1

'''
def getEventsWithFootAVShankAngVel(row, lastRow, shankAVzColumnName, footAVyColumnName, excel_shank_AVz, excel_foot_AVy, 
                                    frequency, direction, waitRow80, waitRow300, waitRow50) :
    
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
    
    dir = 1
    
    if(direction == 'backward') :
        dir = -1
        
    
    # programStartTime = time.time()
    while (row < lastRow):
        
        #HELLO
        
        row += 1
    
        angularVelocity = excel_shank_AVz[shankAVzColumnName].iloc[row] * 180 / math.pi
            
        footAV = excel_foot_AVy[footAVyColumnName].iloc[row] * dir
        
        #allexcel['row'].append(row)
        #allexcel['value'].append(angularVelocity)
        
        ''' Start setup section '''
        
        if previousAngularVelocity == -1000 and previousFootAV == -1000 :
            previousAngularVelocity = angularVelocity
            
            previousFootAV = footAV
            continue
    
        elif previousDifference == -1000 and previousFootAVDifference == -1000 :
            previousAngularVelocity = angularVelocity
            previousDifference = angularVelocity - previousAngularVelocity
            
            previousFootAV = footAV
            previousFootAVDifference = footAV - previousFootAV
            continue
        
        difference = angularVelocity - previousAngularVelocity
        
        footAVDifference = footAV - previousFootAV
            
        ''' End setup section '''
        
        
        # find minima + negative footAV for MSW
        if(previousFootAVDifference < 0 and footAVDifference > 0 and footAV < 0 and TO == 1) :
            
            if(angularVelocity > 0) :
                data['MSW']['MSW Row'].append(row - 1)
                data['MSW']['MSW Time'].append((row - 1)*((1/frequency)))
                data['MSW']['MSW Angular Velocity'].append(previousAngularVelocity)
                
                MSW = 1
                TO = 0
        
            else :
                # check if there's a max within 50ms (arbitrary time interval)
                startRow = row
                notDone = True
                while (row - startRow < waitRow50 and notDone) :
                    row += 1
                    angularVelocity = excel_shank_AVz[shankAVzColumnName].iloc[row] * 180 / math.pi
                    footAV = excel_foot_AVy[footAVyColumnName].iloc[row] * dir
                    
                    difference = angularVelocity - previousAngularVelocity
                    footAVDifference = footAV - previousFootAV
         
                    if (angularVelocity > 0) :
                        data['MSW']['MSW Row'].append(row - 1)
                        data['MSW']['MSW Time'].append((row - 1)*((1/frequency)))
                        data['MSW']['MSW Angular Velocity'].append(previousAngularVelocity)
                        
                        MSW = 1
                        TO = 0
                        notDone = False
                    
                    previousFootAV = footAV
                    previousFootAVDifference = footAVDifference
                    previousAngularVelocity = angularVelocity
                    previousDifference = difference
                    
                continue
            
            previousFootAV = footAV
            previousFootAVDifference = footAVDifference
            previousAngularVelocity = angularVelocity
            previousDifference = difference
                    
            continue
    
            
    
        # finding HS with Foot AV
        if MSW == 1:
            
            # find a maxima with positive foot AV
            if previousFootAVDifference > 0 and footAVDifference < 0 and footAV > 0:
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
                
            currentTime = row - startTime
            
            if currentTime > waitRow300 :
            
                # find a maxima and positive foot AV
                if previousFootAVDifference > 0 and footAVDifference < 0 and footAV > 1:
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
Frequency at which data is taken:
Participant 4 = 60 Hz
Participant 14 = 60 Hz
Participant 28 = 100Hz
Participant 3 = 60 Hz
'''

def main(participantName, frequency, title):
    
    forwardStartRow, forwardEndRow, backwardStartRow, backwardEndRow, shankAVzColumnName, footAVyColumnName, excel_shank_AVz, excel_foot_AVy = setParticipant(participantName)
    waitRow80 = convertMilliSecToRow(frequency, 80)
    waitRow300 = convertMilliSecToRow(frequency, 300)
    waitRow50 = convertMilliSecToRow(frequency, 50)
    
    directions = ['forward', 'backward']
    
    
    for i in range(2) :
        direction = directions[i]
        startRow = 0
        endRow = 0
        
        if i == 0 :
            startRow = forwardStartRow
            endRow = forwardEndRow
        else :
            startRow = backwardStartRow
            endRow = backwardEndRow
            
        print('\n', direction.capitalize())
      
        gaitEvents = getEventsWithFootAVShankAngVel(startRow, endRow, 
                                                       shankAVzColumnName, footAVyColumnName, 
                                                       excel_shank_AVz, excel_foot_AVy, 
                                                       frequency, direction,
                                                       waitRow80, waitRow300, waitRow50)
    
        MSWdf = DataFrame(gaitEvents[0]['MSW'],columns=['MSW Row', 'MSW Time', 'MSW Angular Velocity'])
        print (MSWdf)
        
        HSdf = DataFrame(gaitEvents[0]['HS'],columns=[ 'HS Row', 'HS Time', 'HS Angular Velocity'])
        print (HSdf)
        
        TOdf = DataFrame(gaitEvents[0]['TO'],columns=[ 'TO Row', 'TO Time', 'TO Angular Velocity'])
        print (TOdf)
        
        fig=plt.figure()
        ax=fig.add_axes([0,0,1,1])
        ax.scatter(gaitEvents[0]['MSW'][ 'MSW Time'], gaitEvents[0]['MSW']['MSW Angular Velocity'], color='r')
        ax.scatter(gaitEvents[0]['HS'][ 'HS Time'], gaitEvents[0]['HS']['HS Angular Velocity'], color='b')
        ax.scatter(gaitEvents[0]['TO'][ 'TO Time'], gaitEvents[0]['TO']['TO Angular Velocity'], color='g')
        
        ax.set_xlabel('Time')
        ax.set_ylabel('AngularVelocity')
        ax.set_title(participantName + direction.capitalize() + title)
        plt.show()
    








if __name__ == "__main__":
    
    #print("60 hz to 300ms = ", convertMilliSecToRow(60, 300), "100 hz to 300ms = ", convertMilliSecToRow(100, 300))
    
    title = ': MSW uses footAV Y < 0 + footAV Y min w/ shank AV > 0 within 50ms'
    
    print('\nPARTICIPANT 4-01\n')
    main('p401', 60, title)
    
    print('\nPARTICIPANT 4-02\n')
    main('p402', 60, title)
    
    print('\nPARTICIPANT 28-01\n')
    main('p2801', 100, title)
    
    print('\nPARTICIPANT 28-02\n')
    main('p2802', 100, title)
    
    print('\nPARTICIPANT 3-03\n')
    main('p303', 60, title)
    
    print('\nPARTICIPANT 31-03\n')
    main('p3103', 100, title)
    
    
    '''
    ^ CHECK (1) PARTICIPANT NAME, 
            (2) FREQUENCY, 
            (3) TITLE ABOVE
    '''
