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
    


def test_print_sensor_quaternions(self, data):
    # Test print
    if self.iteration % 100 == 0:
        qw = data[self.NodeNum_pelvis]['Quat1']
        qx = data[self.NodeNum_pelvis]['Quat2']
        qy = data[self.NodeNum_pelvis]['Quat3']
        qz = data[self.NodeNum_pelvis]['Quat4']
        this_Euler = quat2euler([qw,qx,qy,qz])
        print("sensor pelvis [roll(X) pitch(Y) yaw(Z)]")
        print(np.around(this_Euler,decimals=3))
        print("")
        
    if self.iteration % 100 == 0:
        qw = data[self.NodeNum_thigh]['Quat1']
        qx = data[self.NodeNum_thigh]['Quat2']
        qy = data[self.NodeNum_thigh]['Quat3']
        qz = data[self.NodeNum_thigh]['Quat4']
        this_Euler = quat2euler([qw,qx,qy,qz])
        print("sensor thigh [roll(X) pitch(Y) yaw(Z)]")
        print(np.around(this_Euler,decimals=3))
        print("")

    if self.iteration % 100 == 0:
        qw = data[self.NodeNum_foot]['Quat1']
        qx = data[self.NodeNum_foot]['Quat2']
        qy = data[self.NodeNum_foot]['Quat3']
        qz = data[self.NodeNum_foot]['Quat4']
        this_Euler = quat2euler([qw,qx,qy,qz])
        print("sensor foot [roll(X) pitch(Y) yaw(Z)]")
        print(np.around(this_Euler,decimals=3))
        print("")
        


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
    
    GB_Euler0_target = [0,0,CommonYaw]  # this is our alignment target, we expect rotate IMU to this orientation, both pelvis and thigh have the same target.
    GB_q0_target = euler2quat(GB_Euler0_target)  # target in quaternion format.    
    
    GS_q0 = GS_pelvis_q0  # current IMU orientation, in global coordinate.
    BS_q_pelvis_inv = quat_multiply(quat_conj(GS_q0),GB_q0_target)  # conjugate quaternion of thigh sensor to segment quaternion. inv represent for inversion, the same as conjugate. 
    # refer to Hip angle tutorial SageMotion.pptx step2.
    
    GS_q0 = GS_thigh_q0  
    BS_q_thigh_inv = quat_multiply(quat_conj(GS_q0),GB_q0_target)
    
    print("Calibrate finished")



def calculate_HipExtAngle(data, initialQuat):
    
    GS_pelvis_q0 = [
                    initialQuat['pelvis_q0'],
                    initialQuat['pelvis_q1'],
                    initialQuat['pelvis_q2'],
                    initialQuat['pelvis_q3'] ]
    GS_thigh_q0 = [
                    initialQuat['upperLeg_q0'],
                    initialQuat['upperLeg_q1'],
                    initialQuat['upperLeg_q2'],
                    initialQuat['upperLeg_q3'] ]

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
    
    ## From calibration ##
    
    pelvis_Euler = quat2euler(GS_pelvis_q0)
    CommonYaw = pelvis_Euler[2]
    
    GB_Euler0_target = [0,0,CommonYaw]  
    # ^ this is our alignment target, we expect rotate IMU to this orientation, 
    # both pelvis and thigh have the same target.
    GB_q0_target = euler2quat(GB_Euler0_target)  # target in quaternion format.    
    
    GS_q0 = GS_pelvis_q0  # current IMU orientation, in global coordinate.
    BS_q_pelvis_inv = quat_multiply(quat_conj(GS_q0),GB_q0_target)  # conjugate quaternion of thigh sensor to segment quaternion. inv represent for inversion, the same as conjugate. 
    # refer to Hip angle tutorial SageMotion.pptx step2.
    
    GS_q0 = GS_thigh_q0  
    BS_q_thigh_inv = quat_multiply(quat_conj(GS_q0),GB_q0_target)
    
    ## End calibration ##
    
    
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




    

def main(participantName, frequency, hipThreshold):
    
    # Participant information below
    pathToFolder = '/Users/shana/Desktop/DesktopItems/BIOFEEDBACK/data/'
    
    
    ''' OLD CODE
    
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
            'p2802' : [700, 2240, 2362, 4000, pathToFolder + 'Data/Participant028-002.xlsx'],
            'p303' : [400, 1500, 1588, 2638, pathToFolder + 'Participant003-003.xlsx'],
            'p3103' : [490, 3648, 3845, 7186, pathToFolder + 'Participant031-003.xlsx'], 
              }
    
    
    print("start getting excel")
    
    excel_quat_pelvis_q0 = pandas.read_excel(trials[participantName][FILEPATH_INDEX], 
                                        sheet_name='Segment Orientation - Quat', 
                                        usecols=[1])
    excel_quat_pelvis_q1 = pandas.read_excel(trials[participantName][FILEPATH_INDEX], 
                                        sheet_name='Segment Orientation - Quat', 
                                        usecols=[2])
    excel_quat_pelvis_q2 = pandas.read_excel(trials[participantName][FILEPATH_INDEX], 
                                        sheet_name='Segment Orientation - Quat', 
                                        usecols=[3])
    excel_quat_pelvis_q3 = pandas.read_excel(trials[participantName][FILEPATH_INDEX], 
                                        sheet_name='Segment Orientation - Quat', 
                                        usecols=[4])
    
    print("got pelvis quat columns")
    
    # Right Upper Leg
    excel_quat_upperLeg_q0 = pandas.read_excel(trials[participantName][FILEPATH_INDEX], 
                                        sheet_name='Segment Orientation - Quat', 
                                        usecols=[61])
    excel_quat_upperLeg_q1 = pandas.read_excel(trials[participantName][FILEPATH_INDEX], 
                                        sheet_name='Segment Orientation - Quat', 
                                        usecols=[62])
    excel_quat_upperLeg_q2 = pandas.read_excel(trials[participantName][FILEPATH_INDEX], 
                                        sheet_name='Segment Orientation - Quat', 
                                        usecols=[63])
    excel_quat_upperLeg_q3 = pandas.read_excel(trials[participantName][FILEPATH_INDEX], 
                                        sheet_name='Segment Orientation - Quat', 
                                        usecols=[64])
    # XSENS hip angle
    excel_hipZXY_flexion = pandas.read_excel(trials[participantName][FILEPATH_INDEX], 
                                             sheet_name='Joint Angles ZXY', 
                                             usecols=[45])

    print("got upper leg (thigh) quat columns")
    
    
    row = trials[participantName][FORWARD_START_ROW]
    lastRow = trials[participantName][BACKWARD_END_ROW]
    '''
    
    
    sageMotionData = '/Users/shana/Downloads/SageMotionSupport20210402/hip joint trial16.xlsx'
    
    print("start getting excel")
    
    sheetName = 'Sheet1'
    
    excel_quat_pelvis_q0 = pandas.read_excel(sageMotionData, 
                                        sheet_name=sheetName, 
                                        usecols=[44])
    excel_quat_pelvis_q1 = pandas.read_excel(sageMotionData, 
                                        sheet_name=sheetName, 
                                        usecols=[45])
    excel_quat_pelvis_q2 = pandas.read_excel(sageMotionData, 
                                        sheet_name=sheetName, 
                                        usecols=[46])
    excel_quat_pelvis_q3 = pandas.read_excel(sageMotionData, 
                                        sheet_name=sheetName, 
                                        usecols=[47])
    
    print("got pelvis quat columns")
    
    # Right Upper Leg
    excel_quat_upperLeg_q0 = pandas.read_excel(sageMotionData, 
                                        sheet_name=sheetName, 
                                        usecols=[28])
    excel_quat_upperLeg_q1 = pandas.read_excel(sageMotionData, 
                                        sheet_name=sheetName, 
                                        usecols=[29])
    excel_quat_upperLeg_q2 = pandas.read_excel(sageMotionData, 
                                        sheet_name=sheetName, 
                                        usecols=[30])
    excel_quat_upperLeg_q3 = pandas.read_excel(sageMotionData, 
                                        sheet_name=sheetName, 
                                        usecols=[31])
    
    
    row = 0
    lastRow = 2195
    
    hipData = { 'Calculated' : { 'Row' : [], 'Joint Angle' : [] },
                'Actual' : { 'Row' : [], 'Joint Angle' : [] },
               }
    
    initialQuat = { 
                'pelvis_q0' : excel_quat_pelvis_q0['Quat1_3'].iloc[row], 
                'pelvis_q1' : excel_quat_pelvis_q1['Quat2_3'].iloc[row],
                'pelvis_q2' : excel_quat_pelvis_q2['Quat3_3'].iloc[row],
                'pelvis_q3' : excel_quat_pelvis_q3['Quat4_3'].iloc[row],
                
                'upperLeg_q0' : excel_quat_upperLeg_q0['Quat1_2'].iloc[row],
                'upperLeg_q1' : excel_quat_upperLeg_q1['Quat2_2'].iloc[row],
                'upperLeg_q2' : excel_quat_upperLeg_q2['Quat3_2'].iloc[row],
                'upperLeg_q3' : excel_quat_upperLeg_q3['Quat4_2'].iloc[row]
                }
    
    while(row < lastRow):
        
        ''' OLD CODE
        
        pelvis_q0 = excel_quat_pelvis_q0['Pelvis q0'].iloc[row]
        pelvis_q1 = excel_quat_pelvis_q1['Pelvis q1'].iloc[row]
        pelvis_q2 = excel_quat_pelvis_q2['Pelvis q2'].iloc[row]
        pelvis_q3 = excel_quat_pelvis_q3['Pelvis q3'].iloc[row]
        
        
        upperLeg_q0 = excel_quat_upperLeg_q0['Right Upper Leg q0'].iloc[row]
        upperLeg_q1 = excel_quat_upperLeg_q1['Right Upper Leg q1'].iloc[row]
        upperLeg_q2 = excel_quat_upperLeg_q2['Right Upper Leg q2'].iloc[row]
        upperLeg_q3 = excel_quat_upperLeg_q3['Right Upper Leg q3'].iloc[row]
        
        actualHip = excel_hipZXY_flexion['Right Hip Flexion/Extension'].iloc[row]
        
        q_pelvis = pyq.Quaternion(pelvis_q0,pelvis_q1,pelvis_q2,pelvis_q3)
        q_upperLeg = pyq.Quaternion(upperLeg_q0,upperLeg_q1,upperLeg_q2,upperLeg_q3)
        '''
        
        data = { 
                'pelvis_q0' : excel_quat_pelvis_q0['Quat1_3'].iloc[row], 
                'pelvis_q1' : excel_quat_pelvis_q1['Quat2_3'].iloc[row],
                'pelvis_q2' : excel_quat_pelvis_q2['Quat3_3'].iloc[row],
                'pelvis_q3' : excel_quat_pelvis_q3['Quat4_3'].iloc[row],
                
                'upperLeg_q0' : excel_quat_upperLeg_q0['Quat1_2'].iloc[row],
                'upperLeg_q1' : excel_quat_upperLeg_q1['Quat2_2'].iloc[row],
                'upperLeg_q2' : excel_quat_upperLeg_q2['Quat3_2'].iloc[row],
                'upperLeg_q3' : excel_quat_upperLeg_q3['Quat4_2'].iloc[row]
                }
        
        
        #self.iteration += 1
        
        # Test print sensor quaternions
        #HipExt_funcs.test_print_sensor_quaternions(self,data)
        
        # Calibrate to find BS_q, sensor to body segment alignment quaternions on 1st iteration
        #if self.iteration == 1:
        if row == 0:
            calibrate(data) 

        # Find the gait phase
        #HipExt_funcs.update_gaitphase(self,self.NodeNum_foot,data)

        # Calculate hip extension angle
        (Hip_flex, Hip_abd, Hip_rot) = calculate_HipExtAngle(data, initialQuat) #     
        
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
                   
        #self.my_sage.save_data(data, my_data)
        print(Hip_flex)
        addData(hipData, 'Calculated', [row/frequency, Hip_flex])
        #self.my_sage.send_stream_data(data, my_data)
        
        ## end SageMotion code
        
        
        # Get the difference between these two orientations
       ## q_hipAngle = q_pelvis.conjugate * q_upperLeg
        
        # Euler Angle
       #theta = math.asin ( 2 * (q_hipAngle.w * q_hipAngle.y - q_hipAngle.z * q_hipAngle.x) )
        
       # addData(hipData, 'Calculated', [row, -theta*180.0/math.pi])
       # addData(hipData, 'Actual', [row, actualHip])
        
        row += 1
        
        
   # graph hip angles
    graph(hipData, 0, 0, 
                  participantName, 'Hip Calculations', 
                  'Row', 'Hip Flexion/Extension', 
                  ['Calculated'], 
                  ['Row', 'Joint Angle'], ['g'])
    
    

    
if __name__ == "__main__":
    
    hipThreshold = -10
    
    main('SageMotion data', 100, hipThreshold)
    
    #print('\nPARTICIPANT 4-01\n')
    #main('p401', 60, hipThreshold)
    
    #print('\nPARTICIPANT 4-02\n')
    #main('p402', 60, hipThreshold)
    
    #print('\nPARTICIPANT 28-01\n')
    #main('p2801', 100, hipThreshold)
    
    #print('\nPARTICIPANT 28-02\n')
    #main('p2802', 100, hipThreshold)
    
    #print('\nPARTICIPANT 3-03\n')
    #main('p303', 60, hipThreshold)
    
    #print('\nPARTICIPANT 31-03\n')
    #main('p3103', 100, hipThreshold)
    
    
    '''
    ^ CHECK (1) PARTICIPANT NAME, 
            (2) FREQUENCY
            (3) in main(), change the pathToFolder
    '''
    
    
    