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


p401InputLength = 2691
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




# Returns a dictionary of the entire dataset's mean, max, and upper mean values
#
# Uses the global variable 'columnName' and 'excel_data_df'
def findDFstats(currentRow, lastRow):
    
    while (currentRow < lastRow) :
        angularVelocity = excel_data_df[columnName].iloc[currentRow] * 180 / math.pi
        
        allexcel['row'].append(currentRow)
        allexcel['value'].append(angularVelocity)
        
        currentRow += 1
        
    allexcelDF = DataFrame(allexcel, columns=['row', 'value'])
    mean = allexcelDF['value'].mean(axis=0)
    max = allexcelDF['value'].max(axis=0)
    
    valuesGreaterThanMeanDF = allexcelDF[allexcelDF['value'] > mean]
    upperMean = valuesGreaterThanMeanDF['value'].mean(axis=0)
    
    valuesLessThanMeanDF = allexcelDF[allexcelDF['value'] < mean]
    lowerMean = valuesLessThanMeanDF['value'].mean(axis=0)
    
    return {'mean' : mean, 'max' : max, 'upperMean' : upperMean, 'lowerMean' : lowerMean}
    



# Start main code
    
# contains mean, max and upper mean of the entire data
stats = findDFstats(row, inputLength)

print("Mean =", stats['mean'], "\nMax Value =", stats['max'], "\nupperMean =", stats['upperMean'], "\nlowerMean =", stats['lowerMean'])


prevMax = -1000.0
prevMin = 1000.0


th1 = 0.6 * stats['max']
th2 = 0.8 * stats['upperMean']
th4 = 0.8 * stats['lowerMean']
th3 = abs(th4)
th6 = 2 * th3


while(row < inputLength):
    
    # setup variables 
    
    angularVelocity = excel_data_df[columnName].iloc[row] * 180 / math.pi
    
    if previousAngularVelocity == -1000 :
        previousAngularVelocity = angularVelocity
        continue

    elif previousDifference == -1000 :
        previousDifference = angularVelocity - previousAngularVelocity
        previousAngularVelocity = angularVelocity
        continue
    
    difference = angularVelocity - previousAngularVelocity
    
    
    # start body of the code
    
    # conditions for MSW: max, th2
    if (previousDifference > 0 and difference < 0 ):
        
        prevMax = angularVelocity
        
        # solve for th1 condition
        if (prevMin <= (0.4 * angularVelocity)
        and angularVelocity > th2 ):
            
            # if less than 0.5 seconds, then keep the higher value
            if ( len(data['MSW']['MSW Row']) > 0
            and (row - data['MSW']['MSW Row'][-1]) < 30 ):
                
                # less than 0.5s and current val is higher
                # else if current val is not higher, do nothing
                if (data['MSW']['MSW Angular Velocity'][-1] < angularVelocity):
                    data['MSW']['MSW Row'].pop()
                    data['MSW']['MSW Time'].pop()
                    data['MSW']['MSW Angular Velocity'].pop()

                    data['MSW']['MSW Row'].append(row)
                    data['MSW']['MSW Time'].append((row)*((1/60)))
                    data['MSW']['MSW Angular Velocity'].append(angularVelocity)
            
            # if not less than 0.5 seconds, just add it
            else:
                
                data['MSW']['MSW Row'].append(row)
                data['MSW']['MSW Time'].append((row)*((1/60)))
                data['MSW']['MSW Angular Velocity'].append(angularVelocity)
           
    
    # is a minima
    if previousDifference < 0 and difference > 0:
        
        prevMin = angularVelocity
        
        #HS < mean & preceding max th3 condition & < mean
        if (angularVelocity < stats['mean']
        and prevMax >= (angularVelocity + th3) ):
            data['HS']['HS Row'].append(row)
            data['HS']['HS Time'].append(row*(1/60))
            data['HS']['HS Angular Velocity'].append(angularVelocity)
            
            
        #TO th6 and th4
        if (prevMax >= (angularVelocity + th6)
        and angularVelocity < th4 ):
            data['TO']['TO Row'].append(row-1)
            data['TO']['TO Time'].append((row-1)*((1/60)))
            data['TO']['TO Angular Velocity'].append(previousAngularVelocity)
    
    
    # setup for next loop
    
    previousAngularVelocity = angularVelocity
    previousDifference = difference
    
    row += 1
    


pandas.set_option("display.max_rows", None, "display.max_columns", None)


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
ax.set_title('AT: 4-01')
plt.show()

'''

^ CHANGE THE AX.SET_TITLE ABOVE

'''



        