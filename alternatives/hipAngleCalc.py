import pandas
from pandas import DataFrame
import matplotlib.pyplot as plt
# pip install pyquaternion
import pyquaternion as pyq
import math
import numpy as np


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
        
        ax.scatter(data[dataTypesNames[i]][columnNames[0]], data[dataTypesNames[i]][columnNames[1]], color=colors[i])
    
    ax.set_xlabel(xLabel)
    ax.set_ylabel(yLabel)
    ax.set_title(participantName + " " +  title)
    plt.axvline(x = (forwardEnd + backwardStart) / 2)
    plt.show()
        
    
    
'''
Inputs:
    - sheetName: excel sheet name
    - startingColumn: column for q0, assuming that the rest of the quaternion columns appear sequentially after
'''
def getExcelQuaternions(filepath, sheetName, startingColumn):
    
    quat = []
    
    for i in range(0, 4):
        quat.append( pandas.read_excel(filepath, sheet_name=sheetName, usecols=[startingColumn + i]) )

    return quat[0], quat[1], quat[2], quat[3]  

    
    

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
    
    print("start getting excel")
    
    excel_quat_pelvis = getExcelQuaternions(trials[participantName][FILEPATH_INDEX], 'Segment Orientation - Quat', 1)

    
    print("got pelvis quat columns")
    
    # Right Upper Leg
    excel_quat_upperLeg = getExcelQuaternions(trials[participantName][FILEPATH_INDEX], 'Segment Orientation - Quat', 61)


    # XSENS hip angle
    excel_hipZXY_flexion = pandas.read_excel(trials[participantName][FILEPATH_INDEX], 
                                             sheet_name='Joint Angles ZXY', 
                                             usecols=[45])

    print("got upper leg (thigh) quat columns")
    
    
    row = trials[participantName][FORWARD_START_ROW]
    lastRow = trials[participantName][BACKWARD_END_ROW]
    
    ''' # SAGE MOTION DATA
    
    sageMotionData = '/Users/shana/Downloads/SageMotionSupport20210402/hip joint trial16.xlsx'
    
    print("start getting excel")
    
    sheetName = 'Sheet1'
    
    excel_quat_pelvis = getExcelQuaternions(sageMotionData, sheetName, 44)
    
    print("got pelvis quat columns")
    
    # Right Upper Leg
    excel_quat_upperLeg = getExcelQuaternions(sageMotionData, sheetName, 28)
    
    
    row = 0
    lastRow = 2195
    '''
    
    hipData = { 'Calculated' : { 'Row' : [], 'Joint Angle' : [] },
                'Actual' : { 'Row' : [], 'Joint Angle' : [] },
                'Roll' : { 'Row' : [], 'Joint Angle' : [] },
                'Pitch' : { 'Row' : [], 'Joint Angle' : [] },
                'Yaw' : { 'Row' : [], 'Joint Angle' : [] },
               }
    
    while(row < lastRow):
        
        pelvis_q0 = excel_quat_pelvis[0]['Pelvis q0'].iloc[row]
        pelvis_q1 = excel_quat_pelvis[1]['Pelvis q1'].iloc[row]
        pelvis_q2 = excel_quat_pelvis[2]['Pelvis q2'].iloc[row]
        pelvis_q3 = excel_quat_pelvis[3]['Pelvis q3'].iloc[row]
        
        
        upperLeg_q0 = excel_quat_upperLeg[0]['Right Upper Leg q0'].iloc[row]
        upperLeg_q1 = excel_quat_upperLeg[1]['Right Upper Leg q1'].iloc[row]
        upperLeg_q2 = excel_quat_upperLeg[2]['Right Upper Leg q2'].iloc[row]
        upperLeg_q3 = excel_quat_upperLeg[3]['Right Upper Leg q3'].iloc[row]
        
        ''' # SAGE MOTION DATA
        pelvis_q0 = excel_quat_pelvis[0]['Quat1_3'].iloc[row] 
        pelvis_q1 = excel_quat_pelvis[1]['Quat2_3'].iloc[row]
        pelvis_q2 = excel_quat_pelvis[2]['Quat3_3'].iloc[row]
        pelvis_q3 = excel_quat_pelvis[3]['Quat4_3'].iloc[row]
        
        upperLeg_q0 = excel_quat_upperLeg[0]['Quat1_2'].iloc[row]
        upperLeg_q1 = excel_quat_upperLeg[1]['Quat2_2'].iloc[row]
        upperLeg_q2 = excel_quat_upperLeg[2]['Quat3_2'].iloc[row]
        upperLeg_q3 = excel_quat_upperLeg[3]['Quat4_2'].iloc[row]
        '''
        
        #actualHip = excel_hipZXY_flexion['Right Hip Flexion/Extension'].iloc[row]
        
        # Hip angle calculation from https://stackoverflow.com/questions/57063595/how-to-obtain-the-angle-between-two-quaternions
        q_pelvis = pyq.Quaternion(pelvis_q0,pelvis_q1,pelvis_q2,pelvis_q3)
        q_upperLeg = pyq.Quaternion(upperLeg_q0,upperLeg_q1,upperLeg_q2,upperLeg_q3)
        
        # Get the difference between these two orientations
        q_hipAngle = q_pelvis.conjugate * q_upperLeg
        
        '''
        # Euler ZYX
        phi   = x = math.atan2( 2 * (qd.w * qd.x + qd.y * qd.z), 1 - 2 * (qd.x**2 + qd.y**2) )
        theta = y = math.asin ( 2 * (qd.w * qd.y - qd.z * qd.x) )
        psi   = z = math.atan2( 2 * (qd.w * qd.z + qd.x * qd.y), 1 - 2 * (qd.y**2 + qd.z**2) )
        
        '''
        '''
        # Euler Angle
        theta = math.asin ( 2 * (q_hipAngle.w * q_hipAngle.y - q_hipAngle.z * q_hipAngle.x) )
        
        
        
        print(row, " --> ", theta)
        print(theta*180.0/math.pi)
        
        addData(hipData, 'Calculated', [row, -theta*180.0/math.pi])
        addData(hipData, 'Actual', [row, actualHip])
        '''
        
        # From XSENS manual
        # w x y z
        # 0 1 2 3
        rollTop = (2 * q_hipAngle.y * q_hipAngle.z) + (2 * q_hipAngle.w * q_hipAngle.x)
        rollBottom = (2 * q_hipAngle.w * q_hipAngle.w) + (2 * q_hipAngle.z * q_hipAngle.z) - 1
        roll = math.atan2(rollTop, rollBottom)
        
        pitch = -math.asin( (2 * q_hipAngle.x * q_hipAngle.z) - (2 * q_hipAngle.w * q_hipAngle.y) )
        
        yawTop = (2 * q_hipAngle.x * q_hipAngle.y) + (2 * q_hipAngle.w * q_hipAngle.z)
        yawBottom = (2 * q_hipAngle.w * q_hipAngle.w) + (2 * q_hipAngle.x * q_hipAngle.x) - 1
        yaw = math.atan2(yawTop, yawBottom)
        
        #addData(hipData, 'Calculated', [row, yaw])
        #addData(hipData, 'Actual', [row, actualHip])
        
        #addData(hipData, 'Roll', [row, roll])
        addData(hipData, 'Pitch', [row, pitch])
        #addData(hipData, 'Yaw', [row, yaw])
        
        
        row += 1
        
        
    # graph hip angles
    graph(hipData, 0, 0,
    #graph(hipData, trials[participantName][FORWARD_END_ROW], trials[participantName][BACKWARD_START_ROW], 
                  participantName, 'w/ Old Code', 
                  'Row', 'Roll w/ XSENS', 
                  ['Roll'], 
                  ['Row', 'Joint Angle'], ['g'])
    
    graph(hipData, 0, 0,
    #graph(hipData, trials[participantName][FORWARD_END_ROW], trials[participantName][BACKWARD_START_ROW], 
                  participantName, 'w/ Old Code', 
                  'Row', 'Pitch w/ XSENS', 
                  ['Pitch'], 
                  ['Row', 'Joint Angle'], ['b'])
    
    graph(hipData, 0, 0,
    #graph(hipData, trials[participantName][FORWARD_END_ROW], trials[participantName][BACKWARD_START_ROW], 
                  participantName, 'w/ Old Code', 
                  'Row', 'Yaw w/ XSENS', 
                  ['Yaw'], 
                  ['Row', 'Joint Angle'], ['r'])
    
    
    

    
if __name__ == "__main__":
    
    hipThreshold = -10
    '''
    main('SageMotion data', 100, hipThreshold)
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
    
    '''
    ^ CHECK (1) PARTICIPANT NAME, 
            (2) FREQUENCY
            (3) in main(), change the pathToFolder
    '''
