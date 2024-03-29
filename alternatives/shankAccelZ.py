# -*- coding: utf-8 -*-
import time
import pandas
from pandas import DataFrame
import matplotlib.pyplot as plt



'''
To clean up:
- participant 14 AV

Possible issues:
- some angular velocity might not have the prior peaks
- some gait cycles might not meet threshold
- wait time to find the minima is arbitrary


Ideas:
- just compare maximas greater than 4.9 [doesn't work] 
- another check: upper leg z is increasing? [nope] and maybe negative 

Notes:
- 300ms after HS is detected, biofeedback starts checking hip angles and code 
  searches for next HS

'''




# Convert data collection frequency to milliseconds
def convertMilliSecToRow(frequency, milliseconds):
    seconds = milliseconds / 1000
    return seconds * frequency



'''
Graphs for one direction

Inputs:
    - data: a dictionary that holds dictionary values
    e.g.) { 'MSW' : { 'Row' : [0,1,2..], 'Time' : [...] },
           'HS' : { 'Row' : [0,1,2..], 'Time' : [...] } }
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
def graph(data, forwardEnd, backwardStart, participantName, title, xLabel, yLabel, dataTypesNames, columnNames, colors) :
    
    fig=plt.figure()
    ax=fig.add_axes([0,0,1,1])
    
    for i in range(len(dataTypesNames)) :
        
        # print only the gait event data, not hip angle
        if dataTypesNames[i] == 'HS':
            print( participantName, " - ", dataTypesNames[i], "\n", DataFrame(data['HS'], columns = columnNames) )
        
        ax.scatter(data[dataTypesNames[i]][columnNames[1]], data[dataTypesNames[i]][columnNames[2]], color=colors[i])
    
    ax.set_xlabel(xLabel)
    ax.set_ylabel(yLabel)
    ax.set_title(participantName + " " +  title)
    plt.axvline(x = (forwardEnd + backwardStart) / 2)
    plt.show()
    
    

'''
Adds data to a dictionary dataset

Inputs:
    - data: a dictionary that holds dictionary values
    e.g.) { 'MSW' : { 'Row' : [0,1,2..], 'Time' : [...] },
           'HS' : { 'Row' : [0,1,2..], 'Time' : [...] } }
    - key: main key in the dictionary 
    e.g.) 'MSW' and 'HS' in the example above
    - arrayOfInputs: array of data to add
    e.g.) [1, 2] would add 1 to 'Row' and 2 to 'Time'
'''
def addData(data, key, arrayOfInputs):
    
    i = 0
    for subkey in data[key]:
        data[key][subkey].append(arrayOfInputs[i])
        i += 1
    return data




'''
Calculates gait events with Shank Acceleration and checks Hip Angle

NOTES: 
    - has indication for direction, but not really necessary
    - waitRowArbitrary is an arbitrary value wait time that seems to work with our participants

HS conditions:
    - Keep track of all maximas > 2 
    - If maxima is > 4.9 (half G) and taller than previous maxima, then during the waitRowArbitrary 
      time frame, look for a negative minima, and mark the next row was HS
    - Wait 300ms (do nothing) before looking for next heel strike and look at hip angle
'''
def getEventsWithShankAccelZ(row, lastRow, hipThreshold,
                                   shankAccelZColumnName, hipZXYFlexionColumnName,
                                   excel_shank_AccelZ, excel_hipZXY_flexion, 
                                   frequency, direction, waitRow80, waitRow300, waitRowArbitrary60) :
    
    
    previousShankAccelZ = -1000.0
    previousShankAccelZDifference = -1000.0
    
    previousShankAccelZMax = 0
    
    HSStartRow = 10000
    
    data = { 'all' : {'Row': [], 'Time' : [], 'Angular Velocity' : []},
            'HS' : {'Row': [], 'Time' : [], 'Angular Velocity' : []} }
    
    hipData = { 'All Hip Values' : { 'Row' : [], 'Time' : [], 'Joint Angle' : [] },
               'Crossed Threshold' : { 'Row' : [], 'Time' : [], 'Joint Angle' : [] }
               }
        
    biofeedbackStatus = 'OFF' 
    
    # programStartTime = time.time()
    while (row < lastRow):
        
        row += 1
    
        shankAccelZ = excel_shank_AccelZ[shankAccelZColumnName].iloc[row]      
        
            
        hipAngle = excel_hipZXY_flexion[hipZXYFlexionColumnName].iloc[row]
        
        
        addData(data, 'all', [row, row/frequency, shankAccelZ])
        addData(hipData, 'All Hip Values', [row, row/frequency, hipAngle])
        
        
        ''' Start setup section '''
        
        if previousShankAccelZ == -1000 :
            previousShankAccelZ = shankAccelZ
            
            continue
    
        elif previousShankAccelZDifference == -1000 :
            #swap these two :0
            previousShankAccelZ = shankAccelZ 
            previousShankAccelZDifference = shankAccelZ - previousShankAccelZ 
            
            continue
        
        shankAccelZDifference = shankAccelZ - previousShankAccelZ
        
        
        ''' Check hip angle '''
        
        
        if hipAngle < hipThreshold and biofeedbackStatus == 'OFF' :
            biofeedbackStatus = 'ON'
            print("BIOFEEDBACK ", biofeedbackStatus, " - ", row)
            addData(hipData, 'Crossed Threshold', [row, row/frequency, hipAngle])
            
        # Just for graphing/collecting data
        elif hipAngle < hipThreshold and biofeedbackStatus == 'ON' :
            addData(hipData, 'Crossed Threshold', [row, row/frequency, hipAngle])
            
        elif hipAngle > hipThreshold and biofeedbackStatus == 'ON' :
            biofeedbackStatus = 'OFF'
            print("BIOFEEDBACK ", biofeedbackStatus, " - ", row)
        

        
        # Might have a high overhead since we are reassigning it at a lot of maximas?
        # Maxima greater than 2
        if previousShankAccelZDifference > 0 and shankAccelZDifference < 0 and previousShankAccelZ > 2 :
            
            # Greater than 4.9 and is > to previous max --> set previous max value and look for HS
            if previousShankAccelZ > 4.9 and previousShankAccelZ > previousShankAccelZMax :
                
                previousShankAccelZMax = previousShankAccelZ 

                startRow = row
                notDone = True
                
                # Search for waitRowArbirtrary time frame for a negative minima
                while row - startRow < waitRowArbitrary60 and notDone :
                    row += 1
                    shankAccelZ = excel_shank_AccelZ[shankAccelZColumnName].iloc[row]
                    
                    shankAccelZDifference = shankAccelZ - previousShankAccelZ
                    
                    hipAngle = excel_hipZXY_flexion[hipZXYFlexionColumnName].iloc[row]
                    
                    addData(data, 'all', [row, row/frequency, shankAccelZ])
                    addData(hipData, 'All Hip Values', [row, row/frequency, hipAngle])
         
                    # Found a minima
                    if previousShankAccelZDifference < 0 and shankAccelZDifference > 0:
                        
                         # must be a negative minima, if not negative, then it's not HS and end the loop
                        if previousShankAccelZ < 0 :
                            
                            addData(data, 'HS', [row, row/frequency, shankAccelZ])
                            
                            HSStartRow = row
                            
                            previousShankAccelZ = shankAccelZ
                            previousShankAccelZDifference = shankAccelZDifference
                            
                            # Wait 300 ms before searching for next HS
                            # End one row beforehand so then it can go back to the main loop and increment by 1 row
                            while row - HSStartRow < waitRow300 - 1 and row < lastRow:
                                row += 1
                                
                                shankAccelZ = excel_shank_AccelZ[shankAccelZColumnName].iloc[row]
                    
                                shankAccelZDifference = shankAccelZ - previousShankAccelZ
                                
                                hipAngle = excel_hipZXY_flexion[hipZXYFlexionColumnName].iloc[row]
                                
                                addData(data, 'all', [row, row/frequency, shankAccelZ])
                                addData(hipData, 'All Hip Values', [row, row/frequency, hipAngle])
                                
                                # Still add maximas > 2
                                if previousShankAccelZDifference > 0 and shankAccelZDifference < 0 and previousShankAccelZ > 2:
                                    previousShankAccelZMax = previousShankAccelZ 
                                
                                previousShankAccelZ = shankAccelZ
                                previousShankAccelZDifference = shankAccelZDifference
                            
                
                        notDone = False
                    
                    else:
                        previousShankAccelZ = shankAccelZ
                        previousShankAccelZDifference = shankAccelZDifference
                
                continue
            
            else:
                previousShankAccelZMax = previousShankAccelZ 


        previousShankAccelZ = shankAccelZ
        previousShankAccelZDifference = shankAccelZDifference
        
    return data, hipData
    
    
    



    
    
    
'''
Combine forward and backward data

Inputs:
    - data: a dictionary that holds dictionary values for either forward or backward
    e.g.) { 'MSW' : { 'Row' : [0,1,2..], 'Time' : [...] },
           'HS' : { 'Row' : [0,1,2..], 'Time' : [...] } }
    - alldata: similar format as above, but will hold both forward and backward data
'''
def combineForwardAndBackward(data, alldata):
    
    for key in alldata:
        for subkey in data[key]:
            alldata[key][subkey].extend(data[key][subkey])
            
            
    

'''
Frequency at which data is taken:
Participant 4 = 60 Hz
Participant 14 = 60 Hz
Participant 28 = 100Hz
Participant 3 = 60 Hz
Participant 31 = 100 Hz
'''

def main(participantName, frequency, hipThreshold):
    
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
            # turnaround point is unknown
            'p1401' : [50, -1, -1, 1136, 'Right Lower Leg Angular Velocity (from radians)', pathToFolder + 'F014-001--Calculated_AV.xlsx'],
            # turnaround point is unknown
            'p1402' : [150, -1, -1, 845, 'Right Lower Leg Angular Velocity (from radians)', pathToFolder + 'F014-002--Calculated_AV.xlsx'],
            'p2801' : [520, 2108, 2209, 3800, pathToFolder + 'Participant028-001.xlsx'],
            'p2802' : [700, 2240, 2362, 4000, pathToFolder + 'Participant028-002.xlsx'],
            'p303' : [400, 1500, 1588, 2638, pathToFolder + 'Participant003-003.xlsx'],
            'p3103' : [490, 3648, 3845, 7186, pathToFolder + 'Participant031-003.xlsx'], 
              }
    
    forwardStartRow = trials[participantName][FORWARD_START_ROW]
    forwardEndRow = trials[participantName][FORWARD_END_ROW]
    backwardStartRow = trials[participantName][BACKWARD_START_ROW]
    backwardEndRow = trials[participantName][BACKWARD_END_ROW]
    
    # When adding another parameter, you need a sheet name and column name
    shankAccelZColumnName = 'Right Lower Leg z'
    hipZXYFlexionColumnName = 'Right Hip Flexion/Extension'
    
    # Excel columns are indexed from zero
    excel_shank_AccelZ = pandas.read_excel(trials[participantName][FILEPATH_INDEX], sheet_name='Segment Acceleration', usecols=[51])
    excel_hipZXY_flexion = pandas.read_excel(trials[participantName][FILEPATH_INDEX], sheet_name='Joint Angles ZXY', usecols=[45])


    
    waitRow80 = convertMilliSecToRow(frequency, 80)
    waitRow300 = convertMilliSecToRow(frequency, 300)
    waitRowArbitrary60 = convertMilliSecToRow(frequency, 60)
    
    
    
    gaitEventsTitle = 'Shank Acceleration z'
    bothGaitDirections = {}
    
    hipTitle = 'Hip ZXY Flexion/Extension'
    allHipData = {}
    
    bothGaitDirections, allHipData = getEventsWithShankAccelZ(forwardStartRow, backwardEndRow, hipThreshold,
                                                       shankAccelZColumnName, hipZXYFlexionColumnName,
                                                       excel_shank_AccelZ, excel_hipZXY_flexion, 
                                                       frequency, 'start to end',
                                                       waitRow80, waitRow300, waitRowArbitrary60)
    
    # graph gait events
    graph(bothGaitDirections, forwardEndRow/frequency, backwardStartRow/frequency, 
                  participantName, gaitEventsTitle, 
                  'Time (s)', 'Shank Accel z', 
                  ['all', 'HS'], 
                  ['Row', 'Time', 'Angular Velocity'], ['g', 'r', 'b'])
    
    # graph hip angles
    graph(allHipData, forwardEndRow/frequency, backwardStartRow/frequency, 
                  participantName, hipTitle, 
                  'Time (s)', 'Hip ZXY Flexion/Extension', 
                  ['All Hip Values', 'Crossed Threshold'], 
                  ['Row', 'Time', 'Joint Angle'], ['g', 'b'])
    
    '''
    ** 
    *
    This commented-out code splits input data into forward and backward chunks, removing the turnaround part 
    *
    **
    
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
        
        gaitEvents, hipData = getEventsWithShankAccelZ(startRow, endRow, hipThreshold,
                                                       shankAccelZColumnName, hipZXYFlexionColumnName,
                                                       excel_shank_AccelZ, excel_hipZXY_flexion, 
                                                       frequency, direction,
                                                       waitRow80, waitRow300, waitRowArbitrary60)
       
        if i == 0:
            bothGaitDirections = gaitEvents
            allHipData = hipData
        else:
            combineForwardAndBackward(gaitEvents, bothGaitDirections)
            combineForwardAndBackward(hipData, allHipData)
    
    
    # graph gait events
    graph(bothGaitDirections, forwardEnd * (1/frequency), backwardStart * (1/frequency), 
                  participantName, gaitEventsTitle, 
                  'Time (s)', 'Shank Accel z', 
                  ['all', 'HS'], 
                  ['Row', 'Time', 'Angular Velocity'], ['g', 'r', 'b'])
    
    # graph hip angles
    graph(allHipData, forwardEnd * (1/frequency), backwardStart * (1/frequency), 
                  participantName, hipTitle, 
                  'Time (s)', 'Hip ZXY Flexion/Extension', 
                  ['All Hip Values', 'Crossed Threshold'], 
                  ['Row', 'Time', 'Joint Angle'], ['g', 'b'])
    '''
    







if __name__ == "__main__":
    
    hipThreshold = -10
    
    print('\nPARTICIPANT 4-01\n')
    main('p401', 60, hipThreshold)
    
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
            (3) in main(), change the pathToFolder
    '''
