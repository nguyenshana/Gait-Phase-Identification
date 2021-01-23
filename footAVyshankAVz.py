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
        footAVyColumnName = 'Right Foot y'
        hipZXYFlexionColumnName = 'Right Hip Flexion/Extension'
        excel_shank_AVz = pandas.read_excel(trials[participant][FILEPATH_INDEX], sheet_name='Segment Angular Velocity', usecols=[51])
        excel_foot_AVy = pandas.read_excel(trials[participant][FILEPATH_INDEX], sheet_name='Segment Angular Velocity', usecols=[53])
        excel_hipZXY_flexion = pandas.read_excel(trials[participant][FILEPATH_INDEX], sheet_name='Joint Angles ZXY', usecols=[45])

    # Participant 14 uses the calculated AV
    else:
        excel_shank_AVz = pandas.read_excel(trials[participant][FILEPATH_INDEX], sheet_name='Segment Angular Velocity', usecols=[4])
    
    return forwardStartRow, forwardEndRow, backwardStartRow, backwardEndRow, shankAVzColumnName, footAVyColumnName, hipZXYFlexionColumnName, excel_shank_AVz, excel_foot_AVy, excel_hipZXY_flexion



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
def getEventsWithFootAVShankAngVel(row, lastRow, hipThreshold,
                                   shankAVzColumnName, footAVyColumnName, hipZXYFlexionColumnName,
                                   excel_shank_AVz, excel_foot_AVy, excel_hipZXY_flexion, 
                                   frequency, direction, waitRow80, waitRow300, waitRow50) :
    
    previousAngularVelocity = -1000.0
    previousDifference = -1000.0
    
    previousFootAV = -1000.0
    previousFootAVDifference = -1000.0
    
    MSW = 0
    HS = 0
    TO = 1
    startTime = 0
    
    data = { 'MSW': {'Row': [], 'Time' : [], 'Angular Velocity' : []},
    'HS' : {'Row': [], 'Time' : [], 'Angular Velocity' : []},
    'TO' : {'Row': [], 'Time' : [], 'Angular Velocity' : []}
    }
    
    #allexcel = { 'row' : [], 'value' : [] }
    
    hipData = { 'All Hip Values' : { 'Row' : [], 'Time' : [], 'Joint Angle' : [] },
               'Crossed Threshold' : { 'Row' : [], 'Time' : [], 'Joint Angle' : [] }
               }
    
    
    dir = 1
    
    if(direction == 'backward') :
        dir = -1
        
    biofeedbackStatus = 'OFF' 
    
    # programStartTime = time.time()
    while (row < lastRow):
        
        row += 1
    
        angularVelocity = excel_shank_AVz[shankAVzColumnName].iloc[row] * 180 / math.pi
            
        footAV = excel_foot_AVy[footAVyColumnName].iloc[row] * dir
        
        hipAngle = excel_hipZXY_flexion[hipZXYFlexionColumnName].iloc[row]
        
        #allexcel['row'].append(row)
        #allexcel['value'].append(angularVelocity)
        hipData['All Hip Values']['Row'].append(row)
        hipData['All Hip Values']['Time'].append(row * (1/frequency))
        hipData['All Hip Values']['Joint Angle'].append(hipAngle)
        
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
            
        
        
        
        ''' Check hip angle '''
        
        # during stance phase, (after HS but before TO), check hip threshold
        if HS == 1 :
            
            if hipAngle < hipThreshold and biofeedbackStatus == 'OFF' :
                biofeedbackStatus = 'ON'
                print("BIOFEEDBACK ", biofeedbackStatus, " - ", row)
                hipData['Crossed Threshold']['Row'].append(row)
                hipData['Crossed Threshold']['Time'].append(row * (1/frequency))
                hipData['Crossed Threshold']['Joint Angle'].append(hipAngle)
                
            elif hipAngle < hipThreshold and biofeedbackStatus == 'ON' :
                hipData['Crossed Threshold']['Row'].append(row)
                hipData['Crossed Threshold']['Time'].append(row * (1/frequency))
                hipData['Crossed Threshold']['Joint Angle'].append(hipAngle)
                
            elif hipAngle > hipThreshold and biofeedbackStatus == 'ON' :
                biofeedbackStatus = 'OFF'
                print("BIOFEEDBACK ", biofeedbackStatus, " - ", row)
        

        
        
        # find minima + negative footAV for MSW
        if (previousFootAVDifference < 0 and footAVDifference > 0 and footAV < 0 and TO == 1) :
            
            if angularVelocity > 0 :
                data['MSW']['Row'].append(row - 1)
                data['MSW']['Time'].append((row - 1)*((1/frequency)))
                data['MSW']['Angular Velocity'].append(previousAngularVelocity)
                
                MSW = 1
                TO = 0
        
            else :
                # check if there's a max within 50ms (arbitrary time interval)
                startRow = row
                notDone = True
                while row - startRow < waitRow50 and notDone :
                    row += 1
                    angularVelocity = excel_shank_AVz[shankAVzColumnName].iloc[row] * 180 / math.pi
                    footAV = excel_foot_AVy[footAVyColumnName].iloc[row] * dir
                    
                    difference = angularVelocity - previousAngularVelocity
                    footAVDifference = footAV - previousFootAV
         
                    if angularVelocity > 0 :
                        data['MSW']['Row'].append(row - 1)
                        data['MSW']['Time'].append((row - 1)*((1/frequency)))
                        data['MSW']['Angular Velocity'].append(previousAngularVelocity)
                        
                        MSW = 1
                        TO = 0
                        notDone = False
                    
                    previousFootAV = footAV
                    previousFootAVDifference = footAVDifference
                    previousAngularVelocity = angularVelocity
                    previousDifference = difference
                    
                continue # continue so that the 'previous' values aren't updated again
            
    
        # finding HS with Foot AV
        elif MSW == 1:
            
            # find a maxima with positive foot AV
            if previousFootAVDifference > 0 and footAVDifference < 0 and footAV > 0:
                data['HS']['Row'].append(row - 1)
                data['HS']['Time'].append((row - 1)*(1/frequency))
                data['HS']['Angular Velocity'].append(previousAngularVelocity)
                
                startTime = row
                HS = 1
                MSW = 0
        
        
        # finding TO with Foot AV
        elif HS == 1:
                
            currentTime = row - startTime
            
            # after 300ms, find a maxima and positive foot AV
            if currentTime > waitRow300 and previousFootAVDifference > 0 and footAVDifference < 0 and footAV > 1:
                    
                if biofeedbackStatus == 'ON' :
                    biofeedbackStatus = 'OFF'
                    print("BIOFEEDBACK ", biofeedbackStatus, " - ", row)
                    
                data['TO']['Row'].append(row - 1)
                data['TO']['Time'].append((row - 1)*(1/frequency))
                data['TO']['Angular Velocity'].append(angularVelocity)
                
                TO = 1
                HS = 0
                  
            
        previousFootAV = footAV
        previousFootAVDifference = footAVDifference
        previousAngularVelocity = angularVelocity
        previousDifference = difference
        
    return data, hipData
    
    
    
    
    
    
'''
Graphs for one direction

Inputs:
    - data: a dictionary that holds dictionary values
    e.g.) { 'MSW' : { 'Row' : [0,1,2..], 'Time' : [...] },
           'HS' : { 'Row' : [0,1,2..], 'Time' : [...] } }
    - see documentation for graphCombined(...) for other input parameters
'''
def graph(data, forwardEnd, backwardStart, participantName, title, xLabel, yLabel, dataTypesNames, columnNames, colors) :
    
    fig=plt.figure()
    ax=fig.add_axes([0,0,1,1])
    
    # adding backward values to forward values
    for i in range(len(dataTypesNames)) :
        
        # print the gait events
        if len(dataTypesNames) == 3:
            print( dataTypesNames[i], "\n", DataFrame(data[dataTypesNames[i]], columns = columnNames) )
            
        ax.scatter(data[dataTypesNames[i]][columnNames[1]], data[dataTypesNames[i]][columnNames[2]], color=colors[i])
    
    ax.set_xlabel(xLabel)
    ax.set_ylabel(yLabel)
    ax.set_title(participantName + " " +  title)
    plt.axvline(x = (forwardEnd + backwardStart) / 2)
    plt.show()
    
    
    
'''
Graphs both forward and backward

Inputs:
    - allData: an array of length 2 with dictionary values that hold a dictionary
    e.g.) allData = [ {
                        'MSW' : { 'Row' : [0,1,2..], 'Time' : [...] },
                        'HS' : { 'Row' : [0,1,2..], 'Time' : [...] } 
                      }, # forward values
                      {
                        'MSW' : { 'Row' : [0,1,2..], 'Time' : [...] },
                        'HS' : { 'Row' : [0,1,2..], 'Time' : [...] } 
                      } # backward values
                        ]
    - forwardEnd: the ending time of the forward phase
    - backwardStart: the start time of the backward phase
    - title: title of the graph
    - xLabel: label for the x-axis
    - yLabel: label for the y-axis
    - dataTypesNames: array of 'parent' dictionary keys (e.g. MSW and HS above)
        - 2nd value will be the x-axis and 3rd value will be the y-axis
    - columnNames: array of 'child' dictionary keys (e.g. Row and Time above)
    - colors: array of color values

'''
def graphCombined(allData, forwardEnd, backwardStart, participantName, title, xLabel, yLabel, dataTypesNames, columnNames, colors) :
    
    combinedData = allData[0]

    # adding backward values to forward values
    for i in range(len(dataTypesNames)) :
        
        for columnName in columnNames : 
            
            combinedData[dataTypesNames[i]][columnName].extend(allData[1][dataTypesNames[i]][columnName])
    
    graph(combinedData, forwardEnd, backwardStart, participantName, title, xLabel, yLabel, dataTypesNames, columnNames, colors)
    
    

'''
Frequency at which data is taken:
Participant 4 = 60 Hz
Participant 14 = 60 Hz
Participant 28 = 100Hz
Participant 3 = 60 Hz
'''

def main(participantName, frequency, hipThreshold):
    
    forwardStartRow, forwardEndRow, backwardStartRow, backwardEndRow, shankAVzColumnName, footAVyColumnName, hipZXYFlexionColumnName, excel_shank_AVz, excel_foot_AVy, excel_hipZXY_flexion = setParticipant(participantName)
    waitRow80 = convertMilliSecToRow(frequency, 80)
    waitRow300 = convertMilliSecToRow(frequency, 300)
    waitRow50 = convertMilliSecToRow(frequency, 50)
    
    gaitEventsTitle = 'Shank AV z'
    bothGaitDirections = []
    
    hipTitle = 'Hip ZXY Flexion/Extension'
    allHipData = []
    
    forwardEnd = 0
    backwardStart = 0
    directions = ['forward', 'backward']
    
    for i in range(2) :
        direction = directions[i]
        startRow = 0
        endRow = 0
        
        if i == 0 :
            startRow = forwardStartRow
            endRow = forwardEndRow
            forwardEnd = endRow
        else :
            startRow = backwardStartRow
            endRow = backwardEndRow
            backwardStart = startRow
            
        print('\n', direction.capitalize())
      
        gaitEvents, hipData = getEventsWithFootAVShankAngVel(startRow, endRow, hipThreshold,
                                                       shankAVzColumnName, footAVyColumnName, hipZXYFlexionColumnName,
                                                       excel_shank_AVz, excel_foot_AVy, excel_hipZXY_flexion, 
                                                       frequency, direction,
                                                       waitRow80, waitRow300, waitRow50)
        bothGaitDirections.append(gaitEvents)
        allHipData.append(hipData)
        
    # graph gait events
    graphCombined(bothGaitDirections, forwardEnd * (1/frequency), backwardStart * (1/frequency), 
                  participantName, gaitEventsTitle, 
                  'Time (s)', 'Shank AV z', 
                  ['MSW', 'HS', 'TO'], 
                  ['Row', 'Time', 'Angular Velocity'], ['r', 'g', 'b'])
    
    # graph hip angles
    graphCombined(allHipData, forwardEnd * (1/frequency), backwardStart * (1/frequency), 
                  participantName, hipTitle, 
                  'Time (s)', 'Hip ZXY Flexion/Extension', 
                  ['All Hip Values', 'Crossed Threshold'], 
                  ['Row', 'Time', 'Joint Angle'], ['g', 'b'])







if __name__ == "__main__":
    
    hipThreshold = -10
    
    #print('\nPARTICIPANT 4-01\n')
    #main('p401', 60, hipThreshold)
    
    print('\nPARTICIPANT 4-02\n')
    main('p402', 60, hipThreshold)
    
    print('\nPARTICIPANT 28-01\n')
    main('p2801', 100, hipThreshold)
    
    print('\nPARTICIPANT 28-02\n')
    main('p2802', 100, hipThreshold)
    
    print('\nPARTICIPANT 3-03\n')
    main('p303', 60, hipThreshold)
    
    print('\nPARTICIPANT 31-03\n')
    main('p3103', 100, hipThreshold)
    
    '''
    ^ CHECK (1) PARTICIPANT NAME, 
            (2) FREQUENCY
    '''
