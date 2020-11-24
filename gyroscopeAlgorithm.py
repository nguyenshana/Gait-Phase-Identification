# -*- coding: utf-8 -*-
import time
import pandas
from pandas import DataFrame
import matplotlib.pyplot as plt
import math

# arbitrary values I assume to be impossible
previousAngularVelocity = -1000.0
previousDifference = -1000.0
programIsRunning = True
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

# CHANGING EXCEL INPUT
# 1. staring row amount (right below this comment section)
# 2. add filepath variable if it's not there
# 3. excel_data_df needs to read the new file
# 4. set input length
# 5. ax.set_title at the very end part of code

p401Row = 400
p402Row = p401Row
p1401Row = 50
p1402Row = 150
row = p401Row

'''

^ CHANGE ROW ABOVE

'''

#
# SECTION TO IMPORT AND GET EXCEL STUFF
#

participant401 = '/Users/shana/Desktop/DesktopItems/BIOFEEDBACK/data/Participant004-001.xlsx'
p401ColumnName = 'Right Lower Leg z'
p401CalculatedColumnName = 'Right Lower Leg Angular Velocity (calculated)'

p401MaybeDegreesCalculated = 'colum F *180/PI()'

participant402 = '/Users/shana/Desktop/DesktopItems/BIOFEEDBACK/data/Participant004-002.xlsx'
p402ColumnName = p401ColumnName
p402CalculatedColumnName = p401CalculatedColumnName

p402MaybeDegreesCalculated = 'colum I *180/PI()'


participant1401 = '/Users/shana/Desktop/DesktopItems/BIOFEEDBACK/data/F014-001--Calculated_AV.xlsx'
p1401ColumnName = 'Right Lower Leg Angular Velocity (from radians)'


participant1402 = '/Users/shana/Desktop/DesktopItems/BIOFEEDBACK/data/F014-002--Calculated_AV.xlsx'
p1402ColumnName = p1401ColumnName
# p1402ColumnName = p1401ColumnName
columnName = p401ColumnName
'''

^ CHANGE COLUMN NAME ABOVE

'''

#Columns are indexed from zero

excel_data_df = pandas.read_excel(participant401, sheet_name='Segment Angular Velocity', usecols=[51])
#excel_data_df = pandas.read_excel(participant1401, sheet_name='Segment Angular Velocity', usecols=[4])
#excel_data_df = pandas.read_excel(participant402, sheet_name='Check Angular Velocity', usecols=[7])
'''

^ CHANGE EXCEL_DATA_DF ABOVE

'''


p401InputLength = 2769
p402InputLength = p401InputLength
p1401InputLength = 1136
p1402InputLength = 845
inputLength = p401InputLength
'''
^ CHANGE INPUT LENGTH ABOVE

'''



'''

Actual algorithm below!


'''

'''

Making threshold based off of -20 threshold wouldn't work because the training part would be
inaccurate (gets incorrect values that aren't TO')

TOthreshold = -20
TOmin = 10000
TOmax = -10000
# insert into array with .insert(index, value)
TOvalues = []
TOindex = 0

TOvalues.insert(TOindex, previousAngularVelocity)
TOindex += 1
if TOindex == 5 :
    TOindex = 5
    
if previousAngularVelocity > TOmax :
    TOmax = previousAngularVelocity
elif previousAngularVelocity < TOmin :
    TOmin = previousAngularVelocity
    
if len(TOvalues) == 5 :
    TOthreshold = ( sum(TOvalues) / len(TOvalues) ) + ( (TOmax - TOmin) / 5 )

'''

prevMin = 0
prevMax = 0

# need to check if 100Hz
# programStartTime = time.time()
while (programIsRunning):
    
    row += 1
    
    # terminating condition
    if (row > inputLength) :
        programIsRunning = False
        continue

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
        prevMax = angularVelocity
        # article version without prevAV > 100:
        if(angularVelocity > 100 or previousAngularVelocity > 100) :
        # my version:
        #if(angularVelocity < -150) :
        #if(angularVelocity > 100 or previousAngularVelocity > 100) :
        #if angularVelocity > 100 or previousAngularVelocity > 100 :
            data['MSW']['MSW Row'].append(row - 1)
            data['MSW']['MSW Time'].append((row - 1)*((1/60)))
            data['MSW']['MSW Angular Velocity'].append(previousAngularVelocity)
            

            # added this myself
            MSW = 1
            TO = 0
            previousAngularVelocity = angularVelocity
            previousDifference = difference
            continue


    # finds a minima
    if previousDifference < 0 and difference > 0 :
        
        prevMin = angularVelocity
        # article version:
        if MSW == 1 and angularVelocity < 0 :
        # my version (for miscalculated ang vel):
        # if MSW == 1 and angularVelocity > 0 :
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
            '''
            80 ms
            previous minima
            max closer to it
            then the next 'minima' is below the maxima & negative slope (so when it turns back to increasing)
            '''
            foundMinima = False
            while row - startCount < 5 and not foundMinima:
                
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
                    while not foundMinima and row - startCount < 5 :
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
                    #
                    # if ((time.time() * 1000) - (startTime * 1000)) <= 80 :
                    #
                    # if minima is not found then just use the maxima value
                    # else minima is found, then use the last angular velocity value
                    # old code that I thought was the same as the article, but it sets the current value as the minima instead
                    '''if not isMinima:
                        minima = maxima
                    else:
                        minima = angularVelocity'''

                
                # after this leaves the while loop and goes to the continue, it essentially skips a line
                ''' moved this to the top of the while loop
                row += 1
                previousAngularVelocity = angularVelocity
                previousDifference = difference
                '''
                #the below line was originally at the top of the while loop
                previousAngularVelocity = angularVelocity
                previousDifference = difference

            #
            # 80 ms interval ended
            #
            
            # Code add here: previous angular velocity = HS
            # aka for my code: minima = HS
            data['HS']['HS Row'].append(minimaRow)
            data['HS']['HS Time'].append(minimaRow*(1/60))
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
            if HS == 1 and angularVelocity < -50 and currentTime > 18 :
            # my version:
            #if HS == 1 and previousAngularVelocity > 0 and angularVelocity < 0 and currentTime > 18:
                HS = 0
                TO = 1
                # add here: previousAngularVelocity = TO
                data['TO']['TO Row'].append(row-1)
                data['TO']['TO Time'].append((row-1)*((1/60)))
                data['TO']['TO Angular Velocity'].append(previousAngularVelocity)

                previousAngularVelocity = angularVelocity
                previousDifference = difference
                continue
            
        '''
            
            
    # moved TO detection so it doesn't need to find a minima first
        
    currentTime = row - startTime
    
    # finds crossing from positive ang velocity to negative
    if HS == 1 and previousAngularVelocity > 0 and angularVelocity < 0 and currentTime > 18:
        HS = 0
        TO = 1
        # add here: previousAngularVelocity = TO
        data['TO']['TO Row'].append(row)
        data['TO']['TO Time'].append(row*((1/60)))
        data['TO']['TO Angular Velocity'].append(previousAngularVelocity)

        previousAngularVelocity = angularVelocity
        previousDifference = difference
        continue
    
    '''
    
    
    
            
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

ax.set_xlabel('Time (row * 1/60)')
ax.set_ylabel('AngularVelocity')
#ax.set_title('14-02 (actual data): MSW  < -150 + HS difference is > 0 + TO is < 0 while prev > 0')
ax.set_title('4-01 with OG code but MSW with prevAV > 100 and TO maxima < -50')
plt.show()

'''

^ CHANGE THE AX.SET_TITLE ABOVE

'''


        