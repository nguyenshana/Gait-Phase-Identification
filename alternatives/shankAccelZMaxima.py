import pandas 
from pandas import DataFrame
import matplotlib.pyplot as plt
import math
import numpy as np
import csv

'''
This file is built off of hipCalc-sageMotion.py

Updates:
    - XSENs data is read from csv files
    - Gait detection code is still in progress. Current code considers forward only; 
      if shankAccelZ maxima > 2: 
          during an arbitrary interval, if there is a negative shankAccelZ with 
          positive shankAngVelY, then that's HS; then wait 300ms before 
          searching for next HS

'''


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
    
    '''
    addData(hipData, 'Actual', [row, actualHip])
    

    hipData = { 'Calculated' : { 'Row' : [], 'Joint Angle' : [] },
                'Actual' : { 'Row' : [], 'Joint Angle' : [] },
                'Crossed Threshold' : { 'Row' : [], 'Joint Angle' : [] },
               }
    '''
    
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
    - title: title of the graph
    - xLabel: label for the x-axis
    - yLabel: label for the y-axis
    - dataTypesNames: array of 'parent' dictionary keys (e.g. MSW and HS above)
        - 2nd value will be the x-axis and 3rd value will be the y-axis
    - columnNames: array of 'child' dictionary keys (e.g. Row and Time above)
    - colors: array of color values
'''   
def graph(data, participantName, title, xLabel, yLabel, dataTypesNames, columnNames, colors) :
    
    fig=plt.figure()
    ax=fig.add_axes([0,0,1,1])
    
    for i in range(len(dataTypesNames)) :
        ax.scatter(data[dataTypesNames[i]][columnNames[0]], data[dataTypesNames[i]][columnNames[1]], color=colors[i])
    
    ax.set_xlabel(xLabel)
    ax.set_ylabel(yLabel)
    ax.set_title(participantName + " " +  title)
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



'''
Calculated from XSENS AWINDA manual --> ZXY
Euler angle ZXY has an euler rotation matrix of YXZ

'''
def XSENSquat2euler(q):
    
    pelvis = [ q['pelvis_q0'], q['pelvis_q1'], q['pelvis_q2'], q['pelvis_q3']]
    
    thigh = [ q['upperLeg_q0'], q['upperLeg_q1'], q['upperLeg_q2'], q['upperLeg_q3']]
    
    q = quat_multiply(quat_conj(pelvis), thigh)
    
    # -R23
    t0 = 2*q[2]*q[3] - 2*q[0]*q[2]
    roll = -math.asin(t0)
    
    # Top = R13, Bottom = R33
    t1 = 2*q[1]*q[3] + 2*q[0]*q[2]
    t2 = 2*q[0]*q[0] + 2*q[3]*q[3] - 1
    pitch = math.atan2(t1, t2)
    
    # Top = R21, Bottom = R22
    t3 = 2*q[1]*q[2] + 2*q[0]*q[3]
    t4 = 2*q[0]*q[0] + 2*q[1]*q[1] - 1 
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
    
    # Comment the above and uncomment below for no calibration
    # B_q_hip_angles = quat_multiply(quat_conj(GS_pelvis_q), GS_thigh_q)

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



'''
Converts data collection frequency to milliseconds
'''
def convertMilliSecToRow(frequency, milliseconds):
    seconds = milliseconds / 1000
    return seconds * frequency








'''
Inputs:
    - participantName [type: string]: if XSENS data, then used to get row information; otherwise, this is just used for graph titling
    - frequency [type: number]: refers to data collection freqency (in Hz); used to calculate time from row for graphing
    - [old, sagemotion has new funuction now] isSageMotionData [type: boolean]: true = data is SageMotion's; main() is split into XSENS and Sagemotion's code; some differences are:
        1. file setup with start and end rows
        2. SageMotion uses Hip_ext while XSENS uses -Hip_abd
        3. CURRENTLY, SageMotion doesn't have biofeedback setup
        4. SageMotion graphs calculations + the empty crossed-threshold values (refer to #3) while XSENS graphs calculated, actual, and crossed-threshold values

TO DO:
    - add SageMotion biofeedback
    - change data structure for HS
'''
def main(participantName, frequency):

    
    row = 0
    lastRow = 0
    
    # Participant information below
    pathToFolder = '/Users/shana/Desktop/DesktopItems/BIOFEEDBACK/data/csv/'
    segmentOrientationQuatFile = '-SegmentOrientationQuat.csv'
    jointAngleZXYFile = '-JointAnglesZXY.csv'
    segmentAccelerationFile = '-SegmentAcceleration.csv'
    segmentAngularVelocityFile = '-SegmentAngularVelocity.csv'
    
    
    FORWARD_START_ROW = 0
    FORWARD_END_ROW = 1
    BACKWARD_START_ROW = 2
    BACKWARD_END_ROW = 3
    trials = {
            'p401' : [500, 1528, 1594, 2695], 
            'p402' : [400, 1429, 1513, 2446],
             #turnaround point is unknown
            'p1401' : [50, -1, -1, 1136],
             #turnaround point is unknown
            'p1402' : [150, -1, -1, 845],
            'p2801' : [520, 2108, 2209, 3800],
            'p2802' : [700, 2240, 2362, 4000],
            'p303' : [400, 1500, 1588, 2638],
            'p3103' : [490, 3648, 3845, 7186],
            
            # made forward/backward end/start the same
            'p701' : [60, 900, 60, 900],
            'p801' : [0, 1050, 0, 1050],
            'p905' : [52, 800, 52, 800],
              }
    
    # XSENS CSV FILES SETUP
 
    print("start getting csv")
    
    quat_csv = list(csv.DictReader(open(pathToFolder + participantName + segmentOrientationQuatFile, mode='r')) )
    
    print("got quat columns")
    
    hipAngles_csv = list(csv.DictReader(open(pathToFolder + participantName + jointAngleZXYFile, mode='r')) )

    print("got actual hip angles")
    
    acceleration_csv = list(csv.DictReader(open(pathToFolder + participantName + segmentAccelerationFile, mode='r')) )
    
    print("got acceleration columns")
    
    angularVelocity_csv = list(csv.DictReader(open(pathToFolder + participantName + segmentAngularVelocityFile, mode='r')) )
    
    print("got angular velocity columns")
    
    row = trials[participantName][FORWARD_START_ROW]
    lastRow = trials[participantName][FORWARD_END_ROW]

    # END SECTION --> XSENS CSV FILES SETUP
    
    
    # Set up variables for iterating throuugh the data
    
    gaitData = { 'HS' : { 'Row' : [], 'Shank Accel Z' : [] },
                }
    
    hipData = { 'Calculated' : { 'Row' : [], 'Joint Angle' : [] },
                'Actual' : { 'Row' : [], 'Joint Angle' : [] },
                'Crossed Threshold' : { 'Row' : [], 'Joint Angle' : [] },
               }
    
    initialIteration = True
    secondIteration = False
    
    
    previousHipAngle = -1000.0
    previousHipAngleDifference = -1000.0
    
    previousShankAccelZ = -1000.0
    previousShankAccelZDifference = -1000.0
    previousShankAccelZMax = 0
    
    #NEW
    previousShankAngVelY = -1000.0
    previousShankAngVelYDiifference = -1000.0
    foundNegMinima = False
    
    previousShankAngVelX = -1000.0
    previousShankAngVelXDiifference = -1000.0
    foundPosMaxima = False
    
    #do i need to add HSStartRow?
    
    hipAngleMinimas = []
    
    doBiofeedback = False
    biofeedbackOn = False
    hipThreshold = -1000.0
    
    waitRow80 = convertMilliSecToRow(frequency, 80)
    waitRow300 = convertMilliSecToRow(frequency, 300)
    waitRowArbitrary60 = convertMilliSecToRow(frequency, 60)
    
    # Only used for XSENS data
    actualHip = 0
    
    while(row < lastRow):
        
        row += 1
            
        # XSENS DATA FORMAT
        
        data = {
                'pelvis_q0': float( quat_csv[row]['Pelvis q0'] ),
                'pelvis_q1': float( quat_csv[row]['Pelvis q1'] ),
                'pelvis_q2': float( quat_csv[row]['Pelvis q2'] ),
                'pelvis_q3': float( quat_csv[row]['Pelvis q3'] ),
                
                'upperLeg_q0': float( quat_csv[row]['Right Upper Leg q0'] ),
                'upperLeg_q1': float( quat_csv[row]['Right Upper Leg q1'] ),
                'upperLeg_q2': float( quat_csv[row]['Right Upper Leg q2'] ),
                'upperLeg_q3': float( quat_csv[row]['Right Upper Leg q3'] ),
                
                'shankAccelZ' : float( acceleration_csv[row]['Right Lower Leg z'] ), 
                'shankAngVelY' : float( angularVelocity_csv[row]['Right Lower Leg y'] ),
                'shankAngVelX' : float( angularVelocity_csv[row]['Right Lower Leg x'] ),
                'actualHip' : float( hipAngles_csv[row]['Right Hip Flexion/Extension'] ),
                }
        
        
        #addData(hipData, 'Actual', [row, actualHip])
        hipData['Actual']['Row'].append(row)
        hipData['Actual']['Joint Angle'].append(data['actualHip'])

        
        roll, pitch, yaw = XSENSquat2euler(data) 
        hipAngle = -pitch # -Hip_abd
        
        #addData(hipData, 'Calculated', [row, hipAngle])
        hipData['Calculated']['Row'].append(row)
        hipData['Calculated']['Joint Angle'].append(hipAngle)
        

        # END SECTION --> XSENS DATA FORMAT
        
            

        
        
        # ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~
        
   
        ## SECTION #1: Initial Walk (no biofeedback; just collect hip angle data)
        
        shankAccelZ = data['shankAccelZ']
            
        if initialIteration:
            previousHipAngle = hipAngle
            
            previousShankAccelZ = shankAccelZ
            
            # NEW
            previousShankAngVelY = data['shankAngVelY']
            previousShankAngVelX = data['shankAngVelX']
            
            initialIteration = False
            secondIteration = True
            continue
            
        elif secondIteration:
            previousHipAngleDifference = hipAngle - previousHipAngle
            previousHipAngle = hipAngle
            
            # SWAPPED compared to old shankAccelZ code
            previousShankAccelZDifference = shankAccelZ - previousShankAccelZ 
            previousShankAccelZ = shankAccelZ 
            
            # NEW
            previousShankAngVelYDifference = data['shankAngVelY'] - previousShankAngVelY 
            previousShankAngVelY = data['shankAngVelY']
            previousShankAngVelXDifference = data['shankAngVelX'] - previousShankAngVelX 
            previousShankAngVelX = data['shankAngVelX']
            
            secondIteration = False
            continue
        
        
        # If it reaches here, then it's not the first two rows
        hipAngleDifference = hipAngle - previousHipAngle
        
        shankAccelZDifference = shankAccelZ - previousShankAccelZ
        
        #NEW
        shankAngVelYDifference = data['shankAngVelY'] - previousShankAngVelY 
        shankAngVelXDifference = data['shankAngVelX'] - previousShankAngVelX
        
        
        # Hip Angle minima 
        if previousHipAngleDifference < 0 and hipAngleDifference > 0 and previousHipAngle < 0 :
            hipAngleMinimas.append(previousHipAngle)
        
        
        
        # ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~
        
        
        ## SECTION #2: Biofeedback
        
        if row > ( 
                    ( lastRow - trials[participantName][FORWARD_START_ROW] )/6 + trials[participantName][FORWARD_START_ROW] 
                 ):
            doBiofeedback = True
        
        # If it's SageMotion data, then we'll need to do biofeedback by manually turning it on or off somehow
        
        if doBiofeedback:
            
            if hipThreshold == -1000:
                
                #print("\nHip angle minima values: ",hipAngleMinimas)
                
                # if no minimas found, default threshold is -1
                if len(hipAngleMinimas) == 0:
                    #print("No hip angle minima values")
                    hipAngleMinimas_average = -1
                else:
                    hipAngleMinimas_average = sum(hipAngleMinimas)/len(hipAngleMinimas)
                
                #print('Hip Angle extention (minima) average was ', hipAngleMinimas_average)
                
                '''
                
                
                
                
                
                If the hip angle avg was positive, threshold would be 'increased' in the wrong direction
                
                
                
                
                
                '''
                
                hipAngle_biofeedbackPercentage = 0 #float ( input("What pecentage increase would you like? (ex. 20)\n") )/100
                
                hipThreshold = hipAngleMinimas_average * (1 + hipAngle_biofeedbackPercentage)
                print("Hip threshold is ", hipThreshold, "\n")
            
            
            if hipAngle < hipThreshold and biofeedbackOn == False :
                biofeedbackOn = True
                #print("BIOFEEDBACK ", biofeedbackOn, " - ", row)
                # addData(hipData, 'Crossed Threshold', [row, hipAngle])
                hipData['Crossed Threshold']['Row'].append(row)
                hipData['Crossed Threshold']['Joint Angle'].append(hipAngle)
                
            # Just for graphing/collecting data
            elif hipAngle < hipThreshold and biofeedbackOn == True :
                #addData(hipData, 'Crossed Threshold', [row, hipAngle])
                hipData['Crossed Threshold']['Row'].append(row)
                hipData['Crossed Threshold']['Joint Angle'].append(hipAngle)
                
            elif hipAngle > hipThreshold and biofeedbackOn == True :
                biofeedbackOn = False
                #print("BIOFEEDBACK ", biofeedbackOn, " - ", row)
                
                
               
        # ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~
        
        ## SECTION #3: Detectiing Heel Strike (HS)
        
        
        # If negative minima is found,
        # then first positive maxima is HS
        
        # negative minima
        if not foundNegMinima and previousShankAngVelYDifference < 0 and shankAngVelYDifference > 0 and previousShankAngVelY < 0:
            foundNegMinima = True
            
        # positive maxima for shank ang vel X
        if not foundPosMaxima and previousShankAngVelXDifference > 0 and shankAngVelXDifference < 0 and previousShankAngVelX > 0:
            foundPosMaxima = True
        
        # positive maxima
        if foundNegMinima and foundPosMaxima and previousShankAngVelYDifference > 0 and shankAngVelYDifference < 0 and previousShankAngVelY > 0:
            gaitData['HS']['Row'].append(row)
            gaitData['HS']['Shank Accel Z'].append(shankAccelZ)
            foundNegMinima = False
            foundPosMaxima = False
            
            HSstartRow = row
            
            
            while ( row - HSstartRow < convertMilliSecToRow(frequency, 300) and row < lastRow):
                
                row += 1
            
                # XSENS DATA FORMAT
            
                data = {
                        'pelvis_q0': float( quat_csv[row]['Pelvis q0'] ),
                        'pelvis_q1': float( quat_csv[row]['Pelvis q1'] ),
                        'pelvis_q2': float( quat_csv[row]['Pelvis q2'] ),
                        'pelvis_q3': float( quat_csv[row]['Pelvis q3'] ),
                        
                        'upperLeg_q0': float( quat_csv[row]['Right Upper Leg q0'] ),
                        'upperLeg_q1': float( quat_csv[row]['Right Upper Leg q1'] ),
                        'upperLeg_q2': float( quat_csv[row]['Right Upper Leg q2'] ),
                        'upperLeg_q3': float( quat_csv[row]['Right Upper Leg q3'] ),
                        
                        'shankAccelZ' : float( acceleration_csv[row]['Right Lower Leg z'] ), 
                        'shankAngVelY' : float( angularVelocity_csv[row]['Right Lower Leg y'] ),
                        'shankAngVelX' : float( angularVelocity_csv[row]['Right Lower Leg x'] ),
                        'actualHip' : float( hipAngles_csv[row]['Right Hip Flexion/Extension'] ),
                        }
                
                # ADDING Data
                
                #addData(hipData, 'Actual', [row, actualHip])
                hipData['Actual']['Row'].append(row)
                hipData['Actual']['Joint Angle'].append(data['actualHip'])
        
                
                roll, pitch, yaw = XSENSquat2euler(data) 
                hipAngle = -pitch # -Hip_abd
                
                #addData(hipData, 'Calculated', [row, hipAngle])
                hipData['Calculated']['Row'].append(row)
                hipData['Calculated']['Joint Angle'].append(hipAngle)
                
                
                # CALCULATIONS
                
                hipAngleDifference = hipAngle - previousHipAngle
                
                shankAccelZDifference = shankAccelZ - previousShankAccelZ
                
                #NEW
                shankAngVelYDifference = data['shankAngVelY'] - previousShankAngVelY 
                shankAngVelXDifference = data['shankAngVelX'] - previousShankAngVelX
                
                
                ## SETUP for next loop
                    
                previousHipAngleDifference = hipAngleDifference
                previousHipAngle = hipAngle
                
                previousShankAccelZDifference = shankAccelZDifference    
                previousShankAccelZ = shankAccelZ
                
                
                # NEW
                previousShankAngVelYDifference = data['shankAngVelY'] - previousShankAngVelY
                previousShankAngVelY = data['shankAngVelY']
                previousShankAngVelXDifference = data['shankAngVelX'] - previousShankAngVelX
                previousShankAngVelX = data['shankAngVelX']
                
            continue
            
        
        '''
        # Might have a high overhead since we are reassigning it at a lot of maximas?
        # Maxima greater than 2
        if previousShankAccelZDifference > 0 and shankAccelZDifference < 0 and previousShankAccelZ > 2 :
            
            # Greater than 4.9 --> look for HS
            if previousShankAccelZ > 4.9:

                startRow = row
                notDone = True
                
                # Search for waitRowArbirtrary time frame for a negative value
                while row - startRow < waitRowArbitrary60 and notDone :
        
                    row += 1
            
                    # XSENS DATA FORMAT
                    
                    data = {
                            'pelvis_q0': float( quat_csv[row]['Pelvis q0'] ),
                            'pelvis_q1': float( quat_csv[row]['Pelvis q1'] ),
                            'pelvis_q2': float( quat_csv[row]['Pelvis q2'] ),
                            'pelvis_q3': float( quat_csv[row]['Pelvis q3'] ),
                            
                            'upperLeg_q0': float( quat_csv[row]['Right Upper Leg q0'] ),
                            'upperLeg_q1': float( quat_csv[row]['Right Upper Leg q1'] ),
                            'upperLeg_q2': float( quat_csv[row]['Right Upper Leg q2'] ),
                            'upperLeg_q3': float( quat_csv[row]['Right Upper Leg q3'] ),
                            
                            'shankAccelZ' : float( acceleration_csv[row]['Right Lower Leg z'] ),
                            'shankAngVelY' : float( angularVelocity_csv[row]['Right Lower Leg y'] ),
                            'actualHip' : float( hipAngles_csv[row]['Right Hip Flexion/Extension'] ),
                            }
                    
                    #addData(hipData, 'Actual', [row, actualHip])
                    hipData['Actual']['Row'].append(row)
                    hipData['Actual']['Joint Angle'].append(data['actualHip'])
                    
                    roll, pitch, yaw = XSENSquat2euler(data) 
                    hipAngle = -pitch # -Hip_abd
                    
                    #addData(hipData, 'Calculated', [row, hipAngle])
                    hipData['Calculated']['Row'].append(row)
                    hipData['Calculated']['Joint Angle'].append(hipAngle)
        
                    # END SECTION --> XSENS DATA FORMAT
                    
                    shankAccelZ = data['shankAccelZ']
                    
                    
                    # NEW
                    shankAngVelYDifference = data['shankAngVelY'] - previousShankAngVelY 
                    
                    
                    
                    hipAngleDifference = hipAngle - previousHipAngle
                    shankAccelZDifference = shankAccelZ - previousShankAccelZ
                    
                    
         
                    # shank accel Z becomes negative & shank angular velocity Y is positive (for forward walking)
                    if shankAccelZ < 0 and data['shankAngVelY'] > 0:
                        
                        #addData(gaitData, 'HS', [row, shankAccelZ])
                        gaitData['HS']['Row'].append(row)
                        gaitData['HS']['Shank Accel Z'].append(shankAccelZ)
                        
                        HSStartRow = row
                        
                        previousHipAngleDifference = hipAngleDifference
                        previousHipAngle = hipAngle
                        
                        previousShankAccelZDifference = shankAccelZDifference
                        previousShankAccelZ = shankAccelZ
                        
                        # Wait 300 ms before searching for next HS
                        # End one row beforehand so then it can go back to the main loop and increment by 1 row
                        while row - HSStartRow < waitRow300 - 1 and row < lastRow:
                            
                            row += 1
                            
        
                            # XSENS DATA FORMAT
                            
                            data = {
                                    'pelvis_q0': float( quat_csv[row]['Pelvis q0'] ),
                                    'pelvis_q1': float( quat_csv[row]['Pelvis q1'] ),
                                    'pelvis_q2': float( quat_csv[row]['Pelvis q2'] ),
                                    'pelvis_q3': float( quat_csv[row]['Pelvis q3'] ),
                                    
                                    'upperLeg_q0': float( quat_csv[row]['Right Upper Leg q0'] ),
                                    'upperLeg_q1': float( quat_csv[row]['Right Upper Leg q1'] ),
                                    'upperLeg_q2': float( quat_csv[row]['Right Upper Leg q2'] ),
                                    'upperLeg_q3': float( quat_csv[row]['Right Upper Leg q3'] ),
                                    
                                    'shankAccelZ' : float( acceleration_csv[row]['Right Lower Leg z'] ),
                                    'shankAngVelY' : float( angularVelocity_csv[row]['Right Lower Leg y'] ), 
                                    'actualHip' : float( hipAngles_csv[row]['Right Hip Flexion/Extension'] ),
                                    }
                    
                            #addData(hipData, 'Actual', [row, actualHip])
                            hipData['Actual']['Row'].append(row)
                            hipData['Actual']['Joint Angle'].append(data['actualHip'])
                            
                            roll, pitch, yaw = XSENSquat2euler(data) 
                            hipAngle = -pitch # -Hip_abd
                            
                            #addData(hipData, 'Calculated', [row, hipAngle])
                            hipData['Calculated']['Row'].append(row)
                            hipData['Calculated']['Joint Angle'].append(hipAngle)
                            
                            # END SECTION --> XSENS DATA FORMAT
                    
                            
                            shankAccelZ = data['shankAccelZ']
                            
                            #NEW
                            shankAngVelYDifference = data['shankAngVelY'] - previousShankAngVelY 
                            
                            hipAngleDifference = hipAngle - previousHipAngle
                            shankAccelZDifference = shankAccelZ - previousShankAccelZ
                            
                            
                            # Set previous values and move on to the next row
                            
                            previousHipAngleDifference = hipAngleDifference
                            previousHipAngle = hipAngle
                        
                            previousShankAccelZDifference = shankAccelZDifference    
                            previousShankAccelZ = shankAccelZ
                            
                            # NEW
                            previousShankAngVelYDifference = data['shankAngVelY'] - previousShankAngVelY 
                            previousShankAngVelY = data['shankAngVelY']
                            
                        # done looking for a HS for now
                        notDone = False
                    
                    else:
                        previousHipAngleDifference = hipAngleDifference
                        previousHipAngle = hipAngle
                    
                        previousShankAccelZDifference = shankAccelZDifference    
                        previousShankAccelZ = shankAccelZ
                        
                        # NEW
                        previousShankAngVelYDifference = shankAccelZ - previousShankAngVelY 
                        previousShankAngVelY = data['shankAngVelY']
                
                continue
            
            '''
            
        
        ## SETUP for next loop
                
        previousHipAngleDifference = hipAngleDifference
        previousHipAngle = hipAngle
        
        previousShankAccelZDifference = shankAccelZDifference    
        previousShankAccelZ = shankAccelZ
        
        
        # NEW
        previousShankAngVelYDifference = data['shankAngVelY'] - previousShankAngVelY
        previousShankAngVelY = data['shankAngVelY']
        previousShankAngVelXDifference = data['shankAngVelX'] - previousShankAngVelX
        previousShankAngVelX = data['shankAngVelX']
        

    '''
    gaitData = { 'HS' : { 'Row' : [], 'Shank Accel Z' : [] },
                }
    
    hipData = { 'Calculated' : { 'Row' : [], 'Joint Angle' : [] },
                'Actual' : { 'Row' : [], 'Joint Angle' : [] },
                'Crossed Threshold' : { 'Row' : [], 'Joint Angle' : [] },
               }
    
        
    # PRINT TO A FILE: HS rows, HS accel values, calculated Hip angles
    
    fileName = "%s-Output.txt" % participantName
    with open(fileName, "a") as f:
        
        f.write("\n\n\n\n\n\n%s HIP CALC ROWS\n" % participantName)
        # f.writelines(hipData['Calculated']['Row'])
        for row in hipData['Calculated']['Row']:
            f.write("%d\n" % row)
        
        f.write("\n\n\n\n\n\n%s HIP CALC VALUES\n" % participantName)
        # f.writelines(hipData['Calculated']['Joint Angle'])
        for angle in hipData['Calculated']['Joint Angle']:
            f.write("%f\n" % angle)
            
        f.write("\n\n\n\n\n\n%s HIP ACTUAL ROWS ROWS\n" % participantName)
        # f.writelines(hipData['Calculated']['Row'])
        for row in hipData['Actual']['Row']:
            f.write("%d\n" % row)
            
        f.write("\n\n\n\n\n\n%s HIP ACTUAL VALUES\n" % participantName)
        # f.writelines(hipData['Calculated']['Joint Angle'])
        for angle in hipData['Actual']['Joint Angle']:
            f.write("%f\n" % angle)
    
        '''
    
    
    
    # PRINT HEEL STRIKE DATA

    for row in gaitData['HS']['Row']:
        print(row)
        
    for accel in gaitData['HS']['Shank Accel Z']:
        print(accel)
        
    
    
    keys = ['Calculated', 'Actual', 'Crossed Threshold']
    colors = ['g', 'b', 'r']
    
    graph(hipData, 
            participantName, 'Hip Calculations (xsens calc ZXY -pitch)', #[XSENS--hip_abd; Sage-hip_ext]
            'Row', 'Hip Flexion/Extension', 
            keys, ['Row', 'Joint Angle'], colors)
    
    





# Not changed to CSV & outdated gait
def getSageMotion(participantName, frequency):

    
    row = 0
    lastRow = 0
    
    
    # SAGEMOTION FILE SETUP
    
    sageMotionData = '/Users/shana/Desktop/DesktopItems/BIOFEEDBACK/SageMotionSupport20210402/hip joint trial16.xlsx'
    
    print("start getting excel")
    
    sheetName = 'Sheet1'
    
    excel_quat_pelvis = getExcelQuaternions(sageMotionData, sheetName, 44)
    
    print("got pelvis quat columns")
    
    # Right Upper Leg
    excel_quat_upperLeg = getExcelQuaternions(sageMotionData, sheetName, 28)
    
    excel_shank_AccelZ = pandas.read_excel(sageMotionData, sheet_name=sheetName, usecols=[5])
    
    print("got shank acceleration Z quat columns")
    
    row = 0
    lastRow = 2180 # was 2195
    

    # END SECTION --> SAGEMOTION FILE SETUP
    
    
    
    # Set up variables for iterating throuugh the data
    
    gaitData = { 'HS' : { 'Row' : [], 'Shank Accel Z' : [] },
                }
    
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
    
    previousShankAccelZ = -1000.0
    previousShankAccelZDifference = -1000.0
    previousShankAccelZMax = 0
    
    #do i need to add HSStartRow?
    
    hipAngleMinimas = []
    
    doBiofeedback = False
    biofeedbackOn = False
    hipThreshold = -1000.0
    
    waitRow80 = convertMilliSecToRow(frequency, 80)
    waitRow300 = convertMilliSecToRow(frequency, 300)
    waitRowArbitrary60 = convertMilliSecToRow(frequency, 60)
    
    # Only used for XSENS data
    actualHip = 0
    
    while(row < lastRow):
        
        row += 1
        
        
        # SAGEMOTION DATA FORMAT
        
        data = { 
                'pelvis_q0' : excel_quat_pelvis[0]['Quat1_3'].iloc[row], 
                'pelvis_q1' : excel_quat_pelvis[1]['Quat2_3'].iloc[row],
                'pelvis_q2' : excel_quat_pelvis[2]['Quat3_3'].iloc[row],
                'pelvis_q3' : excel_quat_pelvis[3]['Quat4_3'].iloc[row],
                
                'upperLeg_q0' : excel_quat_upperLeg[0]['Quat1_2'].iloc[row],
                'upperLeg_q1' : excel_quat_upperLeg[1]['Quat2_2'].iloc[row],
                'upperLeg_q2' : excel_quat_upperLeg[2]['Quat3_2'].iloc[row],
                'upperLeg_q3' : excel_quat_upperLeg[3]['Quat4_2'].iloc[row],
                
                'shankAccelZ' : excel_shank_AccelZ['AccelZ_1'].iloc[row] 
                }
        
        # Lines that start with "###" are parts from SageMotion's code
    
        ### self.iteration += 1
        
        ###  Test print sensor quaternions
        ### HipExt_funcs.test_print_sensor_quaternions(self,data)
        
        ###  Calibrate to find BS_q, sensor to body segment alignment quaternions on 1st iteration
        ### if self.iteration == 1:
        if initialIteration:
            BS_q_pelvis_inv, BS_q_thigh_inv = calibrate(data) 
            # initialIteration = False # added to Section 1 instead

        ### Find the gait phase
        ### HipExt_funcs.update_gaitphase(self,self.NodeNum_foot,data)

        # Calculate hip extension angle
        (Hip_flex, Hip_abd, Hip_rot) = calculate_HipExtAngle(data, BS_q_pelvis_inv, BS_q_thigh_inv) #     
        
        ### Give haptic feedback (turn feedback nodes on/off)
        ### if self.config['isFeedbackOn'] == "Yes" and self.alreadyGivenFeedback == 0:
            ### HipExt_funcs.give_feedback(self) 

        ### time_now = self.iteration / self.DATARATE # time in seconds

        ### my_data = {'time': [time_now],
                   ### 'Gait_Phase': [self.gaitphase]}

        '''
        my_data = {'time': [time_now],
                   'Gait_Phase': [self.gaitphase],
                   'Hip_flex': [Hip_flex],
                   'Hip_abd': [Hip_abd],
                   'Hip_rot': [Hip_rot]}
        '''
        
        hipAngle = Hip_flex
        
        # END SECTION --> SAGEMOTION DATA FORMAT
            
        
        
        ### self.my_sage.save_data(data, my_data)
        ### self.my_sage.send_stream_data(data, my_data)
        addData(hipData, 'Calculated', [row, hipAngle])

        
        
        # ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~
        
   
        ## SECTION #1: Initial Walk (no biofeedback; just collect hip angle data)
        
        shankAccelZ = data['shankAccelZ']
            
        if initialIteration:
            previousHipAngle = hipAngle
            
            previousShankAccelZ = shankAccelZ
            
            initialIteration = False
            secondIteration = True
            continue
            
        elif secondIteration:
            previousHipAngleDifference = hipAngle - previousHipAngle
            previousHipAngle = hipAngle
            
            # SWAPPED compared to old shankAccelZ code
            previousShankAccelZDifference = shankAccelZ - previousShankAccelZ 
            previousShankAccelZ = shankAccelZ 
            
            secondIteration = False
            continue
        
        
        # If it reaches here, then it's not the first two rows
        hipAngleDifference = hipAngle - previousHipAngle
        
        shankAccelZDifference = shankAccelZ - previousShankAccelZ
        
        # Hip Angle minima 
        if previousHipAngleDifference < 0 and hipAngleDifference > 0 and previousHipAngle < 0 :
            hipAngleMinimas.append(previousHipAngle)
        
        
        
        # ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~
        
        
        ## SECTION #2: Biofeedback
        
        # NOT IMPLEMENTED FOR SAGEMOTION DATA
                
                
        # ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~
        
        ## SECTION #3: Detectiing Heel Strike (HS)
        
        # IN PROGRESS, SO NOT IMPLEMENTED FOR SAGEMOTION DATA
        
        
        # ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~
        
        
        ## SETUP for next loop
                
        previousHipAngleDifference = hipAngleDifference
        previousHipAngle = hipAngle
        
        previousShankAccelZDifference = shankAccelZDifference    
        previousShankAccelZ = shankAccelZ
        

            
        
    # Create variables for graphing
    
    startRow = 0
    endRow = 0
    
    keys = ['Calculated', 'Crossed Threshold']
    colors = ['g','r']
    
    
    graph(hipData, 
            participantName, 'Hip Calculations (SageMotion)', #[XSENS--hip_abd; Sage-hip_ext]
            'Row', 'Hip Flexion/Extension', 
            keys, ['Row', 'Joint Angle'], colors)





   
    

    
if __name__ == "__main__":
    
    
    #getSageMotion('SageMotion data', 100)


    print('\nPARTICIPANT 4-01\n')
    main('p401', 60)
    
    print('\nPARTICIPANT 4-02\n')
    main('p402', 60)
    
    #print('\nPARTICIPANT 14-01\n')
    #main('p1401', 60)
    
    #print('\nPARTICIPANT 14-02\n')
    #main('p1402', 60)
    
    

    print('\nPARTICIPANT 7-01\n')
    main('p701', 60)
    
    print('\nPARTICIPANT 8-01\n')
    main('p801', 60)
    
    print('\nPARTICIPANT 9-05\n')
    main('p905', 60)
    

    print('\nPARTICIPANT 28-01\n')
    main('p2801', 100)

    print('\nPARTICIPANT 28-02\n')
    main('p2802', 100)
    
    print('\nPARTICIPANT 3-03\n')
    main('p303', 60)
    
    print('\nPARTICIPANT 31-03\n')
    main('p3103', 100)
    
    
    '''
    ^ CHECK (1) PARTICIPANT NAME, 
            (2) FREQUENCY
            (3) in main(), change the pathToFolder
    '''
    
    
    
