import pandas



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
         #turnaround point is unknown
        'p1401' : [50, -1, -1, 1136, pathToFolder + 'F014-001--Calculated_AV.xlsx'],
         #turnaround point is unknown
        'p1402' : [150, -1, -1, 845, pathToFolder + 'F014-002--Calculated_AV.xlsx'],
        'p2801' : [520, 2108, 2209, 3800, pathToFolder + 'Participant028-001.xlsx'],
        'p2802' : [700, 2240, 2362, 4000, pathToFolder + 'Participant028-002.xlsx'],
        'p303' : [400, 1500, 1588, 2638, pathToFolder + 'Participant003-003.xlsx'],
        'p3103' : [490, 3648, 3845, 7186, pathToFolder + 'Participant031-003.xlsx'],
        
        'p701' : [60, -1, -1, 900, pathToFolder + 'F007-001.xlsx'],
        'p801' : [0, -1, -1, 1050, pathToFolder + 'F008-001.xlsx'],
        'p905' : [52, -1, -1, 800, pathToFolder + 'F009-005.xlsx'],
          }



participantName = 'p401'



# XSENS hip angle
excel_hipZXY_flexion = pandas.read_excel(trials[participantName][FILEPATH_INDEX], 
                                         sheet_name='Joint Angles ZXY', 
                                         usecols=[45])


row = trials[participantName][FORWARD_START_ROW]
lastRow = trials[participantName][BACKWARD_END_ROW]



hipData = { 'Actual' : { 'Row' : [], 'Joint Angle' : [] }, }


while row < lastRow:

	actualHip = excel_hipZXY_flexion['Right Hip Flexion/Extension'].iloc[row]

	hipData['Actual']['Row'].append(row) 
	hipData['Actual']['Joint Angle'].append(actualHip)

	row += 1



print("ROOOOOOOOOOOOOOOOOOOW")
for row in hipData['Actual']['Row']:
	print(row)



print("JOOOOIIIINNNTT ANNNGLLLLEE")
for angle in hipData['Actual']['Joint Angle']:
	print(angle)






