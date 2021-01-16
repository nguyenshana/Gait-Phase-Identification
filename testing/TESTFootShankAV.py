import time
import pandas
from pandas import DataFrame
import matplotlib.pyplot as plt
import math

 

#  THIS IS A TESTING FILE



# Participant information below

typicalColumnName = 'Right Lower Leg z'
pathToFolder = '/Users/shana/Desktop/DesktopItems/BIOFEEDBACK/data/'

# Format of trials = participantKey : [rowValue, columnName, filePath, lastRow]
START_ROW_INDEX = 0
COLUMN_INDEX = 1
FILEPATH_INDEX = 2
LASTROW_INDEX = 3
trials = {
    # old end was 2769, 1528 (turnaround)
    'p401' : [500, typicalColumnName, pathToFolder + 'Participant004-001.xlsx', 2769],
    # old end was 2769, 1429 (turnaround)
    'p402' : [400, typicalColumnName, pathToFolder + 'Participant004-002.xlsx', 2769],
    'p1401' : [50, 'Right Lower Leg Angular Velocity (from radians)', pathToFolder + 'F014-001--Calculated_AV.xlsx', 1136],
    'p1402' : [150, 'Right Lower Leg Angular Velocity (from radians)', pathToFolder + 'F014-002--Calculated_AV.xlsx', 845],
    #old end was 3800, 2108 (turnaround)
    'p2801' : [520, typicalColumnName, pathToFolder + 'Participant028-001.xlsx', 2108],
    #old end was 4000, 2240 (turnaround)
    'p2802' : [700, typicalColumnName, pathToFolder + 'Participant028-002.xlsx', 2240],
    #old end was 2600, 1500 (turnaround)
    'p303' : [400, typicalColumnName, pathToFolder + 'Participant003-003.xlsx', 1500],
    #old end was 7100, 3648 (turnaround)
    'p3103' : [490, typicalColumnName, pathToFolder + 'Participant031-003.xlsx', 3648],
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
Calculates gait events with Shank AV (MSW) and Foot AV (HS and TO)
AV = Angular Velocity
PROBLEM: 
    - MSW only checks for one direction, so when person turns around (and footAV Y changes), then it won't be detected
    - MSW 50ms is arbitrary (wanted to check 3 extra rows)
    - ALL EVENTS CURRENTLY ADD THE ROW BEFORE, so not exactly 'real time'
TO TRY:
    - try looking for maxima and negative shank AV
    - cases for 'forward' and 'backwards'?
    + fix the 50ms and row thing
    - if most activity is near zero, reset to find MSW again?

(1) MSW conditions: foot AV y minima and negative and shank angular velocity < 0 within 50ms

(2) HS conditions: if last MSW foot AV is positive, find foot AV max; 
if last MSW foot AV is negative, then find foot AV min

(3) TO conditions: wait 300ms after HS; same conditions as HS except foot AV max needs to be > 1 and foot AV min needs
to be < -1

'''
def getEventsWithFootAVShankAngVel(row, columnName, excel_data_df, excel_foot_vel, 
                               footColumnName, inputLength, waitRow80, waitRow300, waitRow50, frequency) :
    
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
        
        #allexcel['row'].append(row)
        #allexcel['value'].append(angularVelocity)
        
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
        if( 
                (
                (previousFootAVDifference < 0 and footAVDifference > 0 and footAV < -1)
                or
                (previousFootAVDifference > 0 and footAVDifference < 0 and footAV > 1)
                )
            and TO == 1) :
            
        # my version (for miscalculated ang vel): 
        # if(TO == 1) :
            # article version without prevAV > 100:
#BELOW AV 
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
                # check if there's a max within 50ms (arbitrary time interval)
                startRow = row
                notDone = True
                while (row - startRow < waitRow50 and notDone) :
                    row += 1
                    angularVelocity = excel_data_df[columnName].iloc[row] * 180 / math.pi
                    footAV = excel_foot_vel[footColumnName].iloc[row]
                    
                    difference = angularVelocity - previousAngularVelocity
                    footAVDifference = footAV - previousFootAV
#BELOW AV         
                    if (angularVelocity > 0) :
                        data['MSW']['MSW Row'].append(row - 1)
                        data['MSW']['MSW Time'].append((row - 1)*((1/frequency)))
                        data['MSW']['MSW Angular Velocity'].append(previousAngularVelocity)
                        
            
                        # added this myself
                        MSW = 1
                        TO = 0
                        notDone = False
                    
                    previousFootAV = footAV
                    previousFootAVDifference = footAVDifference
                    previousAngularVelocity = angularVelocity
                    previousDifference = difference
                    
                        
            continue
    
            
    
        # finding HS with Foot AV
        if MSW == 1 :
            
            MSWfootAV = excel_foot_vel[footColumnName].iloc[data['MSW']['MSW Row'][-1]]
            
            # MSW has a negative foot angular velocity y
            if MSWfootAV < 0 :
            
                # find a maxima with positive foot AV
                if previousFootAVDifference > 0 and footAVDifference < 0 and footAV > 1:
                    data['HS']['HS Row'].append(row - 1)
                    data['HS']['HS Time'].append((row - 1)*(1/frequency))
                    data['HS']['HS Angular Velocity'].append(previousAngularVelocity)
                    
                    startTime = row
                    HS = 1
                    MSW = 0
                    
            else:
                
                # find a min and negative foot AV
                if previousFootAVDifference < 0 and footAVDifference > 0 and footAV < -1:
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
        if HS == 1 :
            
            '''
            
            currentTime = row - startTime
            
            if(
                (
                (previousFootAVDifference > 0 and footAVDifference < 0 and footAV > 1)
                or
                (previousFootAVDifference < 0 and footAVDifference > 0 and footAV < -1)
                )
                and currentTime > waitRow300) :
            
                if(angularVelocity < 0) :
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
            
                else :
                    # check if there's a max within 50ms (arbitrary time interval)
                    startRow = row
                    notDone = True
                    while (row - startRow < waitRow50 and notDone) :
                        row += 1
                        angularVelocity = excel_data_df[columnName].iloc[row] * 180 / math.pi
                        footAV = excel_foot_vel[footColumnName].iloc[row]
                        
                        difference = angularVelocity - previousAngularVelocity
                        footAVDifference = footAV - previousFootAV
         
                        if (angularVelocity < 0) :
                            data['TO']['TO Row'].append(row - 1)
                            data['TO']['TO Time'].append((row - 1)*(1/frequency))
                            data['TO']['TO Angular Velocity'].append(angularVelocity)
                            
                            TO = 1
                            HS = 0
                            notDone = False
                        
                        previousFootAV = footAV
                        previousFootAVDifference = footAVDifference
                        previousAngularVelocity = angularVelocity
                        previousDifference = difference
                        
                
                continue
        
                
            '''
            MSWfootAV = excel_foot_vel[footColumnName].iloc[data['MSW']['MSW Row'][-1]] 
            currentTime = row - startTime
            
            
            # MSW has a negative foot angular velocity y
            if MSWfootAV < 0 and currentTime > waitRow300 :
            
                # find a maxima and positive foot AV
                if previousFootAVDifference > 0 and footAVDifference < 0 and footAV > 1:
                    data['TO']['TO Row'].append(row - 1)
                    data['TO']['TO Time'].append((row - 1)*(1/frequency))
                    data['TO']['TO Angular Velocity'].append(angularVelocity)
                    
                    TO = 1
                    HS = 0
                    
            elif currentTime > waitRow300 :
                
                # find a min and negative foot AV
                if previousFootAVDifference < 0 and footAVDifference > 0 and footAV < -1:
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
    
    
    
    
    
    
    
    
    
    
    

def main(participantName, frequency, title):
    
    print("Only Half-way")
    
    participant = setParticipant(participantName)
    waitRow80 = convertMilliSecToRow(frequency, 80)
    waitRow300 = convertMilliSecToRow(frequency, 300)
    waitRow50 = convertMilliSecToRow(frequency, 50)
    
    '''
    gaitEvents = getEventsWithFootAV(participant[0], participant[1], participant[2], 
                                             participant[3], participant[4], participant[5], 
                                             waitRow80, waitRow300, frequency)
    '''
    
    gaitEvents = getEventsWithFootAVShankAngVel(participant[0], participant[1], participant[2], 
                                             participant[3], participant[4], participant[5], 
                                             waitRow80, waitRow300, waitRow50, frequency)
    
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
    






'''
Frequency at which data is taken:
Participant 4 = 60 Hz
Participant 14 = 60 Hz
Participant 28 = 100Hz
Participant 3 = 60 Hz
Participant 31 = 100 Hz
'''

if __name__ == "__main__":
    
    #print("60 hz to 300ms = ", convertMilliSecToRow(60, 300), "100 hz to 300ms = ", convertMilliSecToRow(100, 300))
    
    title = ': MSW uses footAV Y < -1 + footAV Y min w/ shank AV > 0 within 50ms \nand TO shank AV < 0 within 50ms \nand HS TOAV > 1 + 50ms + shankAV > 0'
    
    print('\nPARTICIPANT 4-01\n')
    main('p401', 60, title)
    
    print('PARTICIPANT 4-02\n')
    main('p402', 60, title)
    '''
    print('PARTICIPANT 28-01\n')
    main('p2801', 100, title)
    
    print('PARTICIPANT 28-02\n')
    main('p2802', 100, title)
    
    
    print('PARTICIPANT 3-03\n')
    main('p303', 60, title)
    
    print('PARTICIPANT 31-03\n')
    main('p3103', 100, title)
    '''
    
    
    '''
    ^ CHECK (1) PARTICIPANT NAME, 
            (2) FREQUENCY, 
            (3) TITLE ABOVE
    '''

