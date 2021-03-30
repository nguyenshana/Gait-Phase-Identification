import pandas 
from pandas import DataFrame
import matplotlib.pyplot as plt
# pip install pyquaternion
import pyquaternion as pyq
import math
import numpy as np


def addData(data, key, arrayOfInputs):
    
    i = 0
    for subkey in data[key]:
        data[key][subkey].append(arrayOfInputs[i])
        i += 1
    return data

 
    
        
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
    
    # Excel columns are indexed from zero
    excel_quat_L5_q0 = pandas.read_excel(trials[participantName][FILEPATH_INDEX], 
                                        sheet_name='Segment Orientation - Quat', 
                                        usecols=[5])
    excel_quat_L5_q1 = pandas.read_excel(trials[participantName][FILEPATH_INDEX], 
                                        sheet_name='Segment Orientation - Quat', 
                                        usecols=[6])
    excel_quat_L5_q2 = pandas.read_excel(trials[participantName][FILEPATH_INDEX], 
                                        sheet_name='Segment Orientation - Quat', 
                                        usecols=[7])
    excel_quat_L5_q3 = pandas.read_excel(trials[participantName][FILEPATH_INDEX], 
                                        sheet_name='Segment Orientation - Quat', 
                                        usecols=[8])
    
    print("got L5 quat columns")
    
    # thigh = Right Upper Leg
    excel_quat_thigh_q0 = pandas.read_excel(trials[participantName][FILEPATH_INDEX], 
                                        sheet_name='Segment Orientation - Quat', 
                                        usecols=[61])
    excel_quat_thigh_q1 = pandas.read_excel(trials[participantName][FILEPATH_INDEX], 
                                        sheet_name='Segment Orientation - Quat', 
                                        usecols=[62])
    excel_quat_thigh_q2 = pandas.read_excel(trials[participantName][FILEPATH_INDEX], 
                                        sheet_name='Segment Orientation - Quat', 
                                        usecols=[63])
    excel_quat_thigh_q3 = pandas.read_excel(trials[participantName][FILEPATH_INDEX], 
                                        sheet_name='Segment Orientation - Quat', 
                                        usecols=[64])
    # XSENS hip angle
    excel_hipZXY_flexion = pandas.read_excel(trials[participantName][FILEPATH_INDEX], 
                                             sheet_name='Joint Angles ZXY', 
                                             usecols=[45])

    print("got thigh quat columns")
    
    
    '''
    Possible steps:
    (1) align quaternions with the regular original quaternion (?)
    (2) get the angle between the og & new quat for both L5 and thigh ('normalizing')
    (3) get the angle between the two 'normalized' vectors <-- this will become the hip angle
    '''
    
    row = trials[participantName][FORWARD_START_ROW]
    lastRow = trials[participantName][BACKWARD_END_ROW]
    
    hipData = { 'Calculated' : { 'Row' : [], 'Joint Angle' : [] },
                'Actual' : { 'Row' : [], 'Joint Angle' : [] },
               }
    '''
    endAverage = row + 3
    
    lw = 0
    lx = 0
    ly = 0
    lz = 0
    
    tw = 0
    tx = 0
    ty = 0
    tz = 0
    
    while(row <= endAverage):
        lw = lw + excel_quat_L5_q0['L5 q0'].iloc[row]
        lx = lx + excel_quat_L5_q1['L5 q1'].iloc[row]
        ly = ly + excel_quat_L5_q2['L5 q2'].iloc[row]
        lz = lz + excel_quat_L5_q3['L5 q3'].iloc[row]
        
        tw = tw + excel_quat_thigh_q0['Right Upper Leg q0'].iloc[row]
        tx = tx + excel_quat_thigh_q1['Right Upper Leg q1'].iloc[row]
        ty = ty + excel_quat_thigh_q2['Right Upper Leg q2'].iloc[row]
        tz = tz + excel_quat_thigh_q3['Right Upper Leg q3'].iloc[row]
        
        row += 1
        
    lw = lw/3
    lx = lx/3
    ly = ly/3
    lz = lz/3
    
    tw = tw/3
    tx = tx/3
    ty = ty/3
    tz = tz/3
    
    q_L5_norm = pyq.Quaternion(lw,lx,ly,lz) 
    q_thigh_norm = pyq.Quaternion(tw,tx,ty,tz) 
    qd_norm = q_L5_norm.conjugate * q_thigh_norm
    normAngle = qd_norm.degrees
    '''
    print("ROW - ", row)
    
    
    while(row < lastRow):
        
        #print("#", row)
        
        l5w = excel_quat_L5_q0['L5 q0'].iloc[row]
        l5x = excel_quat_L5_q1['L5 q1'].iloc[row]
        l5y = excel_quat_L5_q2['L5 q2'].iloc[row]
        l5z = excel_quat_L5_q3['L5 q3'].iloc[row]
        
        t5w = excel_quat_thigh_q0['Right Upper Leg q0'].iloc[row]
        t5x = excel_quat_thigh_q1['Right Upper Leg q1'].iloc[row]
        t5y = excel_quat_thigh_q2['Right Upper Leg q2'].iloc[row]
        t5z = excel_quat_thigh_q3['Right Upper Leg q3'].iloc[row]
        
        actualHip = excel_hipZXY_flexion['Right Hip Flexion/Extension'].iloc[row]
        
        #STACK OVERFLOW CODE
        
        
        # L5
        q_upper = pyq.Quaternion(l5w,l5x,l5y,l5z)
        # thigh
        q_lower = pyq.Quaternion(t5w,t5x,t5y,t5z)
        
        # Get the 3D difference between these two orientations
        qd = q_upper.conjugate * q_lower
        
        # Calculate Euler angles from this difference quaternion
        phi   = math.atan2( 2 * (qd.w * qd.x + qd.y * qd.z), 1 - 2 * (qd.x**2 + qd.y**2) )
        theta = math.asin ( 2 * (qd.w * qd.y - qd.z * qd.x) )
        psi   = math.atan2( 2 * (qd.w * qd.z + qd.x * qd.y), 1 - 2 * (qd.y**2 + qd.z**2) )
        
        addData(hipData, 'Calculated', [row, -theta*180.0/math.pi])
        addData(hipData, 'Actual', [row, actualHip])
        
        print("row", row, -theta*180.0/math.pi)
        
        
        
        
        ''' 
        MY OLD CODE
        
        
        # Get angle between quat and original
        q_L5_new = pyq.Quaternion(l5w,l5x,l5y,l5z) 
        q_thigh_new = pyq.Quaternion(t5w,t5x,t5y,t5z) 
        
        print("L5 NEW - ", q_L5_new.degrees)
        print("THIGH NEW - ", q_thigh_new.degrees)
        
        q_L5_difference = q_L5_norm.conjugate * q_L5_new
        q_thigh_difference = q_thigh_norm.conjugate * q_thigh_new
        
        
        # No "normalization" to the normal
        # q_L5_difference = pyq.Quaternion(l5w,l5x,l5y,l5z) 
        # q_thigh_difference = pyq.Quaternion(t5w,t5x,t5y,t5z) 
        
        
        # Quaternion with between two quaternions
        # order doesn't matter
        #qd =  q_L5_difference.conjugate * q_thigh_difference  # (graph #6)
        
        print("     L5 DIFFERENCE - ", q_L5_difference.degrees)
        print("     THIGH DIFFERENCE - ", q_thigh_difference.degrees, "\n")
        
        if q_L5_difference.degrees > 0 and q_thigh_difference.degrees < 0 :    
            qd = q_L5_difference.degrees + q_thigh_difference.degrees
        else:
            qd = q_thigh_difference.degrees - q_L5_difference.degrees
        print('           L5 & THIGH difference - ', qd)
        
        addData(hipData, 'Calculated', [row, normAngle - qd])
        addData(hipData, 'Actual', [row, actualHip])
        '''
        
        row += 1
        
    '''
    print("L5 NORM - ", q_L5_norm, q_L5_norm.degrees)
    print("THIGH NORM - ", q_thigh_norm, q_thigh_norm.degrees)
    print("NORM ANGLE = ", normAngle)
    '''
        
        
   # graph hip angles
    graph(hipData, trials[participantName][FORWARD_END_ROW], trials[participantName][BACKWARD_START_ROW], 
                  participantName, 'Hip Calculations theta', 
                  'Row', 'Hip ZXY Flexion/Extension', 
                  ['Calculated','Actual'], 
                  ['Row', 'Joint Angle'], ['g','b'])
    
    

    
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
        
        
    
