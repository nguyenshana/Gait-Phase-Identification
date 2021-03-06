# -*- coding: utf-8 -*-
import time
import pandas
from pandas import DataFrame
import matplotlib.pyplot as plt
import math

# arbitrary values I assume to be impossible
previousAngularVelocity = -1000.0
previousDifference = -1000.0
MSW = 0
HS = 0
TO = 1
startTime = 0
data = { 'MSW': {'MSW Row': [], 'MSW Time' : [], 'MSW Angular Velocity' : []},
    'HS' : {'HS Row': [], 'HS Time' : [], 'HS Angular Velocity' : []},
    'TO' : {'TO Row': [], 'TO Time' : [], 'TO Angular Velocity' : []}
    }

# dataset to hold all excel values
allexcel = { 'row' : [], 'value' : [] }





# Participant information below


typicalColumnName = 'Right Lower Leg z'
pathToFolder = '/Users/shana/Desktop/DesktopItems/BIOFEEDBACK/data/'

# Format of trials = participantKey : [rowValue, columnName, filePath, lastRow]
ROW_INDEX = 0
COLUMN_INDEX = 1
FILEPATH_INDEX = 2
LASTROW_INDEX = 3
trials = {
    'p401' : [400, typicalColumnName, pathToFolder + 'Participant004-001.xlsx', 2769],
    'p402' : [400, typicalColumnName, pathToFolder + 'Participant004-002.xlsx', 2769],
    'p1401' : [50, 'Right Lower Leg Angular Velocity (from radians)', pathToFolder + 'F014-001--Calculated_AV.xlsx', 1136],
    'p1402' : [150, 'Right Lower Leg Angular Velocity (from radians)', pathToFolder + 'F014-002--Calculated_AV.xlsx', 845],
    'p2801' : [520, typicalColumnName, pathToFolder + 'Participant028-001.xlsx', 3800],
    'p2802' : [700, typicalColumnName, pathToFolder + 'Participant028-002.xlsx', 4000],
    'p303' : [400, typicalColumnName, pathToFolder + 'Participant003-003.xlsx', 2600],
          }


row = None;
columnName = None;
inputLength = 0;
excel_data_df = None;


# Input example: 'p401'
def setParticipant(participant):
    global row
    row = trials[participant][ROW_INDEX]
    global columnName 
    columnName = trials[participant][COLUMN_INDEX]
    
    #Columns are indexed from zero
    global excel_data_df
    if (participant != 'p1401' and participant != 'p1402') :
        excel_data_df = pandas.read_excel(trials[participant][FILEPATH_INDEX], sheet_name='Segment Angular Velocity', usecols=[51])
    else:
        excel_data_df = pandas.read_excel(trials[participant][FILEPATH_INDEX], sheet_name='Segment Angular Velocity', usecols=[4])
    global inputLength
    inputLength = trials[participant][LASTROW_INDEX]


def calculate80msToRow(frequency):
    return 0.08 * frequency

def calculate300msToRow(frequency):
    return 0.3 * frequency


# Frequency at which data is taken:
# Participant 4 = 60 Hz
# Participant 14 = 60 Hz
# Participant 28 = 100Hz
# Participant 3 = 60 Hz

frequency = 60
'''
^ CHECK IF CORRECT FREQUENCY IS SET

'''

participant = 'p1401'
'''
^ SET CORRECT PARTICIPANT

'''
setParticipant(participant)
waitRow80 = calculate80msToRow(frequency)
waitRow300 = calculate300msToRow(frequency)








# Actual algorithm below!


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


    # finds a minima
    if previousDifference < 0 and difference > 0 :
        
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
    
    


MSWdf = DataFrame(data['MSW'],columns=['MSW Row', 'MSW Time', 'MSW Angular Velocity'])
MSWdftime = DataFrame(data['MSW'],columns=['MSW Time'])
print (MSWdf)
# MSWdf.plot(x ='MSW Time', y='MSW Angular Velocity', kind = 'scatter')
# plt.show()

HSdf = DataFrame(data['HS'],columns=[ 'HS Row', 'HS Time', 'HS Angular Velocity'])
HSdftime = DataFrame(data['HS'],columns=[ 'HS Time'])
print (HSdf)
# HSdf.plot(x ='HS Time', y='HS Angular Velocity', kind = 'scatter')
# plt.show()

TOdf = DataFrame(data['TO'],columns=[ 'TO Row', 'TO Time', 'TO Angular Velocity'])
TOdftime = DataFrame(data['TO'],columns=['TO Time'])
print (TOdf)
# TOdf.plot(x ='TO Time', y='TO Angular Velocity', kind = 'scatter')
# plt.show()


fig=plt.figure()
ax=fig.add_axes([0,0,1,1])
# ax.scatter(allexcel['row'], allexcel['value'], color='r')
ax.scatter(data['MSW'][ 'MSW Time'], data['MSW']['MSW Angular Velocity'], color='r')
ax.scatter(data['HS'][ 'HS Time'], data['HS']['HS Angular Velocity'], color='b')
ax.scatter(data['TO'][ 'TO Time'], data['TO']['TO Angular Velocity'], color='g')

ax.set_xlabel('Time')
ax.set_ylabel('AngularVelocity')
#ax.set_title('14-02 (actual data): MSW  < -150 + HS difference is > 0 + TO is < 0 while prev > 0')
ax.set_title(participant + ' with OG code but MSW with prevAV > 100 and TO maxima < -50')
plt.show()

'''

^ CHANGE THE AX.SET_TITLE ABOVE

'''


        