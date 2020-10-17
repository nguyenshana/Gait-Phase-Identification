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
IC = 0
TO = 1
startTime = 0;
data = { 'MSW': {'MSW Time' : [], 'MSW Angular Velocity' : []},
    'IC' : {'IC Time' : [], 'IC Angular Velocity' : []},
    'TO' : {'TO Time': [], 'TO Angular Velocity' : []}
    }

# dataset to hold all excel values
allexcel = { 'row' : [], 'value' : [] }

# CHANGING EXCEL INPUT
# 1. staring row amount (right below this comment section)
# 2. filepath variable
# 3. excel_data_df needs to read the new file
# 4. set input length
# 5. chart title


p402Row = 420
p1401Row = 50
p1402Row = p1401Row
row = p1401Row

'''
def getAngularVelocity(input):
    return 1
'''

#
# SECTION TO IMPORT AND GET EXCEL STUFF
#

participant402 = '/Users/shana/Desktop/BIOFEEDBACK/data/Participant004-002.xlsx'
p402ColumnName = 'Right Lower Leg Angular Velocity'
participant1401 = '/Users/shana/Desktop/BIOFEEDBACK/data/F014-001--Added-angular-velocity.xlsx'
p1401ColumnName = 'Right Lower Leg Angular Velocity'
participant1402 = '/Users/shana/Desktop/BIOFEEDBACK/data/F014-002--Added-angular-velocity.xlsx'
# p1402ColumnName = p1401ColumnName
columnName = p1401ColumnName

#excel_data_df = pandas.read_excel(participant402, sheet_name='Segment Angular Velocity', usecols=[51])
excel_data_df = pandas.read_excel(participant1401, sheet_name='Segment Angular Velocity', usecols=[2])


# print the dataframe
# print(excel_data_df)

# getting length of file, but its 2770
# inputLength = len(excel_data_df)


p402InputLength = 2769
p1401InputLength = 1136
p1402InputLength = 850
inputLength = p1401InputLength

# Get the value of row 
# print(excel_data_df['Right Lower Leg z'].iloc[row])


#
#
#


# need to check if 100Hz
# programStartTime = time.time()
while (programIsRunning):
    
    row += 1
    
    # terminating condition
    if (row > inputLength) :
        programIsRunning = False
        continue

    angularVelocity = excel_data_df[columnName].iloc[row] * (180/math.pi)
    
    print(row, angularVelocity)
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
    if(difference < 0 and previousDifference > 0 and TO == 1) :
        if(angularVelocity > 100) :
            data['MSW']['MSW Time'].append(row)
            data['MSW']['MSW Angular Velocity'].append(previousAngularVelocity)
            

            # added this myself
            MSW = 1
            TO = 0
            previousAngularVelocity = angularVelocity
            previousDifference = difference
            continue


    if difference > 0 and previousDifference < 0 :
        if MSW == 1 and angularVelocity < 0 :
            minima = angularVelocity
            # startTime = time.time() # time is in ns
            startCount = row
            # article: 100 hertz ; 80 ms
            # 60 hz = 0.016666... sec
            # 80 ms = 0.08 sec
            # 0.08/0.0166 = 4.8 = around 5 rows
            #while ( (time.time() * 1000) - (startTime * 1000) ) < 80 :
            #
            
            # this is the 80ms loop
            while row - startCount < 5 :
    
                angularVelocity = excel_data_df[columnName].iloc[row] * (180/math.pi)
                difference = angularVelocity - previousAngularVelocity
                
                if previousDifference < 0 and difference > 0 :
                    minima = angularVelocity
                
                
                # if any maxima in 80 ms window and magnitude diff <= 10
                elif previousDifference > 0 and difference < 0 and angularVelocity - minima <= 10 :
                    # Code add here: immediate minima = IC
                    

                    '''
                    80 ms
                    previous minima
                    max closer to it
                    then the next 'minima' is below the maxima & negative slope (so when it turns back to increasing)
                    '''


                    #
                    #while ( excel_data_df['Right Lower Leg z'].iloc[row]  * (180/math.pi) )< possibleMaxima and time <= 80 :
                    #
                    # search for immediate minima, previous diff is negative and diff is positive
                    maxima = angularVelocity
                    isMinima = False;
                    while not minima and row - startCount < 5 :
                        # wait for next input = increase row
                        row += 1
                        previousAngularVelocity = angularVelocity
                        previousDifference = difference
                        
                        angularVelocity = excel_data_df[columnName].iloc[row]  * (180/math.pi)
                        difference = angularVelocity - previousAngularVelocity
                        
                        if previousDifference < 0 and difference > 0 :
                            isMinima = True
                    #
                    # if ((time.time() * 1000) - (startTime * 1000)) <= 80 :
                    #
                    # if minima is not found then just use the maxima value
                    # else minima is found, then use the last angular velocity value
                    if not isMinima:
                        minima = maxima
                    else:
                        minima = angularVelocity

                
                # after this leaves the while loop and goes to the continue, it essentially skips a line
                row += 1
                previousAngularVelocity = angularVelocity
                previousDifference = difference

            #
            # 80 ms interval ended
            #
            
            # Code add here: previous angular velocity = IC
            # aka for my code: minima = IC
            data['IC']['IC Time'].append(row)
            data['IC']['IC Angular Velocity'].append(minima)

            MSW = 0

            #added this myself
            IC = 1
            #
            #startTime = time.time() # time is in ns
            #
            startTime = row
            previousAngularVelocity = angularVelocity
            previousDifference = difference
            # print("4th continue")
            continue
        
        else :
            #
            #currentTimeMiliSec = (time.time() * 1000) - (startTime * 1000)
            #
            currentTime = row - startTime
            #
            #if IC == 1 and angularVelocity < -20 and currentTimeMiliSec > 300 :
            #
            # 300 ms = 0.3 sec
            # 0.3/0.01666 = 18.07
            # 
            if IC == 1 and angularVelocity < -20 and currentTime > 18 :
                IC = 0
                TO = 1
                # add here: previousAngularVelocity = TO
                data['TO']['TO Time'].append(row)
                data['TO']['TO Angular Velocity'].append(previousAngularVelocity)

                previousAngularVelocity = angularVelocity
                previousDifference = difference
                continue
            
    previousAngularVelocity = angularVelocity
    previousDifference = difference



        
'''
print("\n", data['MSW']['MSW Time'])
print(data['MSW']['MSW Angular Velocity'])
print("\n", data['IC']['IC Time'])
print(data['IC']['IC Angular Velocity'])
print("\n", data['TO']['TO Time'])
print(data['TO']['TO Angular Velocity'])
'''




MSWdf = DataFrame(data['MSW'],columns=[ 'MSW Time', 'MSW Angular Velocity'])
print (MSWdf)
# MSWdf.plot(x ='MSW Time', y='MSW Angular Velocity', kind = 'scatter')
# plt.show()

ICdf = DataFrame(data['IC'],columns=[ 'IC Time', 'IC Angular Velocity'])
print (ICdf)
# ICdf.plot(x ='IC Time', y='IC Angular Velocity', kind = 'scatter')
# plt.show()

TOdf = DataFrame(data['TO'],columns=[ 'TO Time', 'TO Angular Velocity'])
print (TOdf)
# TOdf.plot(x ='TO Time', y='TO Angular Velocity', kind = 'scatter')
# plt.show()


fig=plt.figure()
ax=fig.add_axes([0,0,1,1])
# ax.scatter(allexcel['row'], allexcel['value'], color='r')
ax.scatter(data['MSW'][ 'MSW Time'], data['MSW']['MSW Angular Velocity'], color='g')
ax.scatter(data['IC'][ 'IC Time'], data['IC']['IC Angular Velocity'], color='b')
ax.scatter(data['TO'][ 'TO Time'], data['TO']['TO Angular Velocity'], color='g')

ax.set_xlabel('Rows')
ax.set_ylabel('AngularVelocity')
ax.set_title('14-01 Participant')
plt.show()


'''
plt.plot(data['MSW'][ 'MSW Time'], data['MSW']['MSW Angular Velocity'], label="MSW")
plt.plot(data['IC'][ 'IC Time'], data['IC']['IC Angular Velocity'], label="IC")
plt.plot(data['TO'][ 'TO Time'], data['TO']['TO Angular Velocity'], label="TO")

plt.xlabel('Excel Row')
plt.ylabel('Angular Velocity')
plt.legend()
plt.show()
'''
        