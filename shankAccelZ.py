# -*- coding: utf-8 -*-
import time
import pandas
from pandas import DataFrame
import matplotlib.pyplot as plt


'''
To clean up:
- participant 14 AV

To do: 
- time code to see how long it takes

Ideas:
- just compare maximas greater than 4.9 [doesn't work]
- another check: upper leg z is increasing? [nope] and maybe negative 

Notes:
- still keeping forward and backward separate to ignore the noise during the turnaround, 
  but maybe this isn't necessary? I can check this afterwards when the algorithm works properly
- Biofeedback starts checking 300ms after HS is detected, and doesn't stop checking hip angle 
  until another HS is detected

'''





# Participant information below

pathToFolder = '/Users/shana/Desktop/DesktopItems/BIOFEEDBACK/data/'

# Format of trials = participantKey : [rowValue, columnName, filePath, lastRow]
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




# Input example: 'p401'
def setParticipant(participant):
    forwardStartRow = trials[participant][FORWARD_START_ROW]
    forwardEndRow = trials[participant][FORWARD_END_ROW]
    backwardStartRow = trials[participant][BACKWARD_START_ROW]
    backwardEndRow = trials[participant][BACKWARD_END_ROW]
    
    shankAccelZColumnName = 'Right Lower Leg z'
    # When adding another parameter, you need a sheet name and column name
    
    #Columns are indexed from zero
    if (participant != 'p1401' and participant != 'p1402') :
        hipZXYFlexionColumnName = 'Right Hip Flexion/Extension'
        excel_shank_AccelZ = pandas.read_excel(trials[participant][FILEPATH_INDEX], sheet_name='Segment Acceleration', usecols=[51])
        excel_hipZXY_flexion = pandas.read_excel(trials[participant][FILEPATH_INDEX], sheet_name='Joint Angles ZXY', usecols=[45])

    # Doesn't check Participant 14
    
    return forwardStartRow, forwardEndRow, backwardStartRow, backwardEndRow, shankAccelZColumnName, hipZXYFlexionColumnName, excel_shank_AccelZ, excel_hipZXY_flexion



# Convert data collection frequency to milliseconds
def convertMilliSecToRow(frequency, milliseconds):
    seconds = milliseconds / 1000
    return seconds * frequency




'''
Calculates gait events with Shank Acceleration and checks Hip Angle

NOTES: 
    - has indication for direction, but not really necessary
    - waitRowArbitrary is an arbitrary value wait time that seems to work with our participants

HS conditions:
    - Keep track of all maximas > 2 
    - If maxima is > 4.9 (half G) and taller than previous maxima, then during the waitRowArbitrary 
      time frame, look for a negative minima, and mark the next row was HS

'''
def getEventsWithShankAccelZ(row, lastRow, hipThreshold,
                                   shankAccelZColumnName, hipZXYFlexionColumnName,
                                   excel_shank_AccelZ, excel_hipZXY_flexion, 
                                   frequency, direction, waitRow80, waitRow300, waitRowArbitrary60) :
    
    previousShankAccelZ = -1000.0
    previousShankAccelZDifference = -1000.0
    
    previousShankAccelZMax = 0
    
    HSStartRow = 10000
    
    data = { 'MSW': {'Row': [], 'Time' : [], 'Angular Velocity' : []},
    'HS' : {'Row': [], 'Time' : [], 'Angular Velocity' : []},
    'TO' : {'Row': [], 'Time' : [], 'Angular Velocity' : []}
    }
    
    #allexcel = { 'row' : [], 'value' : [] }
    
    hipData = { 'All Hip Values' : { 'Row' : [], 'Time' : [], 'Joint Angle' : [] },
               'Crossed Threshold' : { 'Row' : [], 'Time' : [], 'Joint Angle' : [] }
               }
        
    biofeedbackStatus = 'OFF' 
    
    # programStartTime = time.time()
    while (row < lastRow):
        
        row += 1
    
        shankAccelZ = excel_shank_AccelZ[shankAccelZColumnName].iloc[row]      
        
            
        hipAngle = excel_hipZXY_flexion[hipZXYFlexionColumnName].iloc[row]
        
        
        #allexcel['row'].append(row)
        #allexcel['value'].append(angularVelocity)
        hipData['All Hip Values']['Row'].append(row)
        hipData['All Hip Values']['Time'].append(row * (1/frequency))
        hipData['All Hip Values']['Joint Angle'].append(hipAngle)
        
        
        ''' Start setup section '''
        
        if previousShankAccelZ == -1000 :
            previousShankAccelZ = shankAccelZ
            
            continue
    
        elif previousShankAccelZDifference == -1000 :
            previousShankAccelZ = shankAccelZ 
            previousShankAccelZDifference = shankAccelZ - previousShankAccelZ 
            
            continue
        
        shankAccelZDifference = shankAccelZ - previousShankAccelZ
        
        
        ''' Check hip angle '''
        
        
        # 300ms after HS, check hip angle until the next HS occurs
        if row - HSStartRow > waitRow300 :
            
            if hipAngle < hipThreshold and biofeedbackStatus == 'OFF' :
                biofeedbackStatus = 'ON'
                print("BIOFEEDBACK ", biofeedbackStatus, " - ", row)
                hipData['Crossed Threshold']['Row'].append(row)
                hipData['Crossed Threshold']['Time'].append(row * (1/frequency))
                hipData['Crossed Threshold']['Joint Angle'].append(hipAngle)
                
            # Just for graphing/collecting data
            elif hipAngle < hipThreshold and biofeedbackStatus == 'ON' :
                hipData['Crossed Threshold']['Row'].append(row)
                hipData['Crossed Threshold']['Time'].append(row * (1/frequency))
                hipData['Crossed Threshold']['Joint Angle'].append(hipAngle)
                
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
                
                while row - startRow < waitRowArbitrary60 and notDone :
                    row += 1
                    shankAccelZ = excel_shank_AccelZ[shankAccelZColumnName].iloc[row]
                    
                    shankAccelZDifference = shankAccelZ - previousShankAccelZ
         
                    if previousShankAccelZDifference < 0 and shankAccelZDifference > 0 :
                        # must be a negative minima, if not negative, then it's not right
                        if previousShankAccelZ < 0 :
                            #print(row, " - ", previousShankAccelZDifference, " ", shankAccelZDifference)
                            data['HS']['Row'].append(row)
                            data['HS']['Time'].append((row)*(1/frequency))
                            data['HS']['Angular Velocity'].append(shankAccelZ)
                            
                            HSStartRow = row
                
                        notDone = False
                    
                    previousShankAccelZ = shankAccelZ
                    previousShankAccelZDifference = shankAccelZDifference
                
                continue
            
            else :
                previousShankAccelZMax = previousShankAccelZ 


        previousShankAccelZ = shankAccelZ
        previousShankAccelZDifference = shankAccelZDifference
        
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
Participant 31 = 100 Hz
'''

def main(participantName, frequency, hipThreshold):
    
    forwardStartRow, forwardEndRow, backwardStartRow, backwardEndRow, shankAccelZColumnName, hipZXYFlexionColumnName, excel_shank_AccelZ, excel_hipZXY_flexion = setParticipant(participantName)
    waitRow80 = convertMilliSecToRow(frequency, 80)
    waitRow300 = convertMilliSecToRow(frequency, 300)
    waitRowArbitrary60 = convertMilliSecToRow(frequency, 60)
    
    gaitEventsTitle = 'Shank Acceleration z'
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
      
        gaitEvents, hipData = getEventsWithShankAccelZ(startRow, endRow, hipThreshold,
                                                       shankAccelZColumnName, hipZXYFlexionColumnName,
                                                       excel_shank_AccelZ, excel_hipZXY_flexion, 
                                                       frequency, direction,
                                                       waitRow80, waitRow300, waitRowArbitrary60)
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
    '''
    print('\nPARTICIPANT 4-01\n')
    main('p401', 60, hipThreshold)
    '''
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
