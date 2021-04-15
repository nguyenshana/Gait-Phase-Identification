import pandas
from pandas import DataFrame
import matplotlib.pyplot as plt
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
        
    
    
def quat2euler(q):
    # Input: Quaternion [qw, qx, qy, qz] 
    # Output: ZYX Euler Angle (in degrees) [roll, pitch, yaw]
    
    # ZYX Euler Angle formed by first rotating about the Z axis (yaw), then Y axis (pitch), then X axis (roll)
    # en.wikipedia.org/wiki/Conversion_between_quaternions_and_Euler_angles#Euler_Angles_to_Quaternion_Conversion
    # computergraphics.stackexchange.com/questions/8195/how-to-convert-euler-angles-to-quaternions-and-get-the-same-euler-angles-back-fr

        qw = q[0]
        qx = q[1]
        qy = q[2]
        qz = q[3]
    
        t0 = 2.0*(qw*qx + qy*qz)
        t1 = 1.0 - 2.0*(qx*qx + qy*qy)
        roll = math.atan2(t0, t1)
    
        t2 = 2.0*(qw*qy - qz*qx)
        t2 = 1.0 if t2 > 1.0 else t2 # correct if it is out of range
        t2 = -1.0 if t2 < -1.0 else t2 # correct if it is out of range
        pitch = math.asin(t2)
    
        t3 = 2.0*(qw*qz + qx*qy)
        t4 = 1.0 - 2.0*(qy*qy + qz*qz)
        yaw = math.atan2(t3, t4)
        
        
        # Convert to degrees
        roll = roll*180/np.pi
        pitch = pitch*180/np.pi
        yaw = yaw*180/np.pi
        
        return [roll, pitch, yaw]
    
    
    
    
def quat2eulerXYZ(q):
    # Input: Quaternion [qw, qx, qy, qz] 
    # Output: XYZ Euler Angle (in degrees) [roll, pitch, yaw]
    # modified from quat2euler 
    
    qw = q[0]
    qx = q[1]
    qy = q[2]
    qz = q[3]

    t0 = 2.0*(-qx*qy + qw*qz)
    t1 = 1.0 - 2.0*(qy*qy + qz*qz)
    roll = math.atan2(t0, t1)

    t2 = 2.0*(qx*qz + qw*qy)
    t2 = 1.0 if t2 > 1.0 else t2 # correct if it is out of range
    t2 = -1.0 if t2 < -1.0 else t2 # correct if it is out of range
    pitch = math.asin(t2)

    t3 = 2.0*(-qy*qz + qw*qx)
    t4 = 1.0 - 2.0*(qx*qx + qy*qy)
    yaw = math.atan2(t3, t4)
    
    
    # Convert to degrees
    roll = roll*180/np.pi
    pitch = pitch*180/np.pi
    yaw = yaw*180/np.pi
    
    return [roll, pitch, yaw] 






def euler2quat(EulerAngle):
    # Input: ZYX Euler Angle (in degrees) [roll, pitch, yaw]
    # Output: Quaternion [qw, qx, qy, qz] 
    
    # ZYX Euler Angle formed by first rotating about the Z axis (yaw), then Y axis (pitch), then X axis (roll)
    # en.wikipedia.org/wiki/Conversion_between_quaternions_and_Euler_angles#Euler_Angles_to_Quaternion_Conversion
    # computergraphics.stackexchange.com/questions/8195/how-to-convert-euler-angles-to-quaternions-and-get-the-same-euler-angles-back-fr
    
    roll = EulerAngle[0]*np.pi/180   # X axis rotation, convert to radians
    pitch = EulerAngle[1]*np.pi/180  # Y axis rotation, convert to radians
    yaw = EulerAngle[2]*np.pi/180    # Z axis rotation, convert to radians
    
    qw = np.cos(roll/2) * np.cos(pitch/2) * np.cos(yaw/2) + np.sin(roll/2) * np.sin(pitch/2) * np.sin(yaw/2)
    qx = np.sin(roll/2) * np.cos(pitch/2) * np.cos(yaw/2) - np.cos(roll/2) * np.sin(pitch/2) * np.sin(yaw/2)
    qy = np.cos(roll/2) * np.sin(pitch/2) * np.cos(yaw/2) + np.sin(roll/2) * np.cos(pitch/2) * np.sin(yaw/2)
    qz = np.cos(roll/2) * np.cos(pitch/2) * np.sin(yaw/2) - np.sin(roll/2) * np.sin(pitch/2) * np.cos(yaw/2)

    return [qw, qx, qy, qz]



def quat_multiply(a, b):
    c = []
    c.append(a[0]*b[0]-a[1]*b[1]-a[2]*b[2]-a[3]*b[3])
    c.append(a[0]*b[1]+a[1]*b[0]+a[2]*b[3]-a[3]*b[2])
    c.append(a[0]*b[2]+a[2]*b[0]+a[3]*b[1]-a[1]*b[3])
    c.append(a[0]*b[3]+a[3]*b[0]+a[1]*b[2]-a[2]*b[1])
    return c



def quat_conj(a):
    return [a[0], -a[1], -a[2], -a[3]]   
    
        


def calibrate(data):

    # Find GS_q_init
    GS_pelvis_q_init = [
                    data['pelvis_q0'],
                    data['pelvis_q1'],
                    data['pelvis_q2'],
                    data['pelvis_q3'] 
                    ]
    GS_thigh_q_init = [
                    data['upperLeg_q0'],
                    data['upperLeg_q1'],
                    data['upperLeg_q2'],
                    data['upperLeg_q3']
                    ]
    # self.GS_foot_q_init = [
                    # data[self.NodeNum_foot]['Quat1'],
                    # data[self.NodeNum_foot]['Quat2'],
                    # data[self.NodeNum_foot]['Quat3'],
                    # data[self.NodeNum_foot]['Quat4']]
    
    GS_pelvis_q0 = GS_pelvis_q_init
    GS_thigh_q0 = GS_thigh_q_init
    
    pelvis_Euler = quat2euler(GS_pelvis_q0)
    CommonYaw = pelvis_Euler[2]
    
    GB_Euler0_target = [0,0,CommonYaw]  
    # ^ this is our alignment target, we expect rotate IMU to this orientation, 
    # both pelvis and thigh have the same target.
    GB_q0_target = euler2quat(GB_Euler0_target)  # target in quaternion format.    
    
    GS_q0 = GS_pelvis_q0  # current IMU orientation, in global coordinate.
    BS_q_pelvis_inv = quat_multiply(quat_conj(GS_q0),GB_q0_target)  
    # ^ conjugate quaternion of thigh sensor to segment quaternion...
    # inv represent for inversion, the same as conjugate. 
    # refer to Hip angle tutorial SageMotion.pptx step2.
    
    GS_q0 = GS_thigh_q0  
    BS_q_thigh_inv = quat_multiply(quat_conj(GS_q0),GB_q0_target)
    
    return BS_q_pelvis_inv, BS_q_thigh_inv





def calculate_HipExtAngle(data, BS_q_pelvis_inv, BS_q_thigh_inv):
    
#     print("calculate_HipExtAngle")
    GS_pelvis_q = [
                    data['pelvis_q0'],
                    data['pelvis_q1'],
                    data['pelvis_q2'],
                    data['pelvis_q3'] ]
    GS_thigh_q = [
                    data['upperLeg_q0'],
                    data['upperLeg_q1'],
                    data['upperLeg_q2'],
                    data['upperLeg_q3'] ]
    # self.GS_foot_q = [
                    # data[self.NodeNum_foot]['Quat1'],
                    # data[self.NodeNum_foot]['Quat2'],
                    # data[self.NodeNum_foot]['Quat3'],
                    # data[self.NodeNum_foot]['Quat4']]
    
    GS_q = GS_pelvis_q
    BS_q = BS_q_pelvis_inv
    GB_pelvis_q = quat_multiply(GS_q,BS_q)


    GS_q = GS_thigh_q
    # orientation diff between thigh IMU and segment
    BS_q = BS_q_thigh_inv
    GB_thigh_q = quat_multiply(GS_q,BS_q)

    # calculate three dimensional hip angles
    B_q_hip_angles = quat_multiply(quat_conj(GB_pelvis_q),GB_thigh_q)    

    this_Euler = quat2eulerXYZ(B_q_hip_angles)  # Euler must be XYZ order, which is the same as the definition of hip angle.
    
    Hip_rot = this_Euler[0]   # hip internal rotation.
    Hip_abd = this_Euler[1]   # hip abduction angle.
    Hip_flex = this_Euler[2]  # hip flexion angle. 
    
    # Test print
    '''
    if self.iteration % 100 == 0:
        print("hip angle [roll(X) pitch(Y) yaw(Z)]")
        print(np.around(this_Euler,decimals=3))
        print("")
    '''
        
    
    return (Hip_flex,Hip_abd,Hip_rot)


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
             #turnaround point is unknown
            'p1401' : [50, -1, -1, 1136, 'Right Lower Leg Angular Velocity (from radians)', pathToFolder + 'F014-001--Calculated_AV.xlsx'],
             #turnaround point is unknown
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

    

    
    ''' # SAGEMOTION STUFF
    
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
                'Crossed Threshold' : { 'Row' : [], 'Joint Angle' : [] },
               }
    
    initialIteration = True
    secondIteration = False
    
    BS_q_pelvis_inv = []
    BS_q_thigh_inv = []
    
    previousHipAngle = -1000.0
    previousHipAngleDifference = -1000.0
    
    hipAngleMinimas = []
    
    doBiofeedback = False
    biofeedbackOn = False
    hipThreshold = -1000.0
    
    while(row < lastRow):
        
        data = {
                'pelvis_q0': excel_quat_pelvis[0]['Pelvis q0'].iloc[row],
                'pelvis_q1': excel_quat_pelvis[1]['Pelvis q1'].iloc[row],
                'pelvis_q2': excel_quat_pelvis[2]['Pelvis q2'].iloc[row],
                'pelvis_q3': excel_quat_pelvis[3]['Pelvis q3'].iloc[row],
                
                'upperLeg_q0': excel_quat_upperLeg[0]['Right Upper Leg q0'].iloc[row],
                'upperLeg_q1': excel_quat_upperLeg[1]['Right Upper Leg q1'].iloc[row],
                'upperLeg_q2': excel_quat_upperLeg[2]['Right Upper Leg q2'].iloc[row],
                'upperLeg_q3': excel_quat_upperLeg[3]['Right Upper Leg q3'].iloc[row],
                }

        actualHip = excel_hipZXY_flexion['Right Hip Flexion/Extension'].iloc[row]

        
        
        ''' #SAGEMOTION DATA FORMAT
        
        data = { 
                'pelvis_q0' : excel_quat_pelvis[0]['Quat1_3'].iloc[row], 
                'pelvis_q1' : excel_quat_pelvis[1]['Quat2_3'].iloc[row],
                'pelvis_q2' : excel_quat_pelvis[2]['Quat3_3'].iloc[row],
                'pelvis_q3' : excel_quat_pelvis[3]['Quat4_3'].iloc[row],
                
                'upperLeg_q0' : excel_quat_upperLeg[0]['Quat1_2'].iloc[row],
                'upperLeg_q1' : excel_quat_upperLeg[1]['Quat2_2'].iloc[row],
                'upperLeg_q2' : excel_quat_upperLeg[2]['Quat3_2'].iloc[row],
                'upperLeg_q3' : excel_quat_upperLeg[3]['Quat4_2'].iloc[row]
                }
        '''
        
        
        
        ## START SAGEMOTION CODE
        
        
        #self.iteration += 1
        
        # Test print sensor quaternions
        #HipExt_funcs.test_print_sensor_quaternions(self,data)
        
        # Calibrate to find BS_q, sensor to body segment alignment quaternions on 1st iteration
        #if self.iteration == 1:
        if initialIteration:
            BS_q_pelvis_inv, BS_q_thigh_inv = calibrate(data) 
            # initialIteration = False ## added to Section 1 instead

        # Find the gait phase
        #HipExt_funcs.update_gaitphase(self,self.NodeNum_foot,data)

        # Calculate hip extension angle
        (Hip_flex, Hip_abd, Hip_rot) = calculate_HipExtAngle(data, BS_q_pelvis_inv, BS_q_thigh_inv) #     
        
        # Give haptic feedback (turn feedback nodes on/off)
        # if self.config['isFeedbackOn'] == "Yes" and self.alreadyGivenFeedback == 0:
            # HipExt_funcs.give_feedback(self) # 

        #time_now = self.iteration / self.DATARATE # time in seconds

        # my_data = {'time': [time_now],
                   # 'Gait_Phase': [self.gaitphase]}

        '''
        my_data = {'time': [time_now],
                   'Gait_Phase': [self.gaitphase],
                   'Hip_flex': [Hip_flex],
                   'Hip_abd': [Hip_abd],
                   'Hip_rot': [Hip_rot]}
        '''
        
        hipAngle = -Hip_abd
                   
        #self.my_sage.save_data(data, my_data)
        addData(hipData, 'Calculated', [row, hipAngle])
        addData(hipData, 'Actual', [row, actualHip])
        #self.my_sage.send_stream_data(data, my_data)
        
        
        ## END SAGEMOTION CODE
        
        
        # ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~
        
   
        ## SECTION #1: Calibration (collect hip angle data)
            
        if initialIteration:
            previousHipAngle = hipAngle
            initialIteration = False
            secondIteration = True
            continue
            
        elif secondIteration:
            previousHipAngleDifference = hipAngle - previousHipAngle
            previousHipAngle = hipAngle
            secondIteration = False
            continue
        
        
        # If it reaches here, then it's not the first two rows
        hipAngleDifference = hipAngle - previousHipAngle
        
        # Hip Angle minima 
        if previousHipAngleDifference < 0 and hipAngleDifference > 0 and previousHipAngle < 0 :
            hipAngleMinimas.append(previousHipAngle)
        
        
        
        # ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~
        
        
        ## SECTION #2: Biofeedback
        
        if row > ( 
                    ( lastRow - trials[participantName][FORWARD_START_ROW] )/6 + trials[participantName][FORWARD_START_ROW] 
                 ):
            doBiofeedback = True
        
        
        if doBiofeedback:
            
            if hipThreshold == -1000:
                
                print("\nHip angle minima values: ",hipAngleMinimas)
                
                hipAngleMinimas_average = sum(hipAngleMinimas)/len(hipAngleMinimas)
                
                print('Hip Angle extention (minima) average was ', hipAngleMinimas_average)
                
                hipAngle_biofeedbackPercentage = float ( input("What pecentage increase would you like?\n(ex. 20)\n") )/100
                
                hipThreshold = hipAngleMinimas_average * (1 + hipAngle_biofeedbackPercentage)
                print("Hip threshold is ", hipThreshold, "\n")
            
            
            if hipAngle < hipThreshold and biofeedbackOn == False :
                biofeedbackOn = True
                print("BIOFEEDBACK ", biofeedbackOn, " - ", row)
                addData(hipData, 'Crossed Threshold', [row, hipAngle])
                
            # Just for graphing/collecting data
            elif hipAngle < hipThreshold and biofeedbackOn == True :
                addData(hipData, 'Crossed Threshold', [row, hipAngle])
                
            elif hipAngle > hipThreshold and biofeedbackOn == True :
                biofeedbackOn = False
                print("BIOFEEDBACK ", biofeedbackOn, " - ", row)
                
                
               
        # ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~
        
        
        ## SETUP for next loop
                
        previousHipAngleDifference = hipAngleDifference
        previousHipAngle = hipAngle
        
        row += 1
            
        
        
        
        
    #graph hip angles
    #graph(hipData, 0, 0,
    graph(hipData, trials[participantName][FORWARD_END_ROW], trials[participantName][BACKWARD_START_ROW], 
                  participantName, 'Hip Calculations (-1*hip_abd)', 
                  'Row', 'Hip Flexion/Extension', 
                  ['Calculated', 'Actual','Crossed Threshold'], 
                  ['Row', 'Joint Angle'], ['g','b','r'])
    
    

    
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
    
    
    