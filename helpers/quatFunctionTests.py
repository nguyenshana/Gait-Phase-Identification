import pandas 
from pandas import DataFrame
import matplotlib.pyplot as plt
# pip install pyquaternion
import pyquaternion as pyq
import math
import numpy as np
#import matlab.engine


'''
TEXTBOOK ZXY using astro & tb euler rotation matrix with TB quaternion matrix
- pitch seems to fit the data like how astro yaw fits it (negated; 402 & 3103 scaled up)

'''
def tbZXYtbEulerTBquat(q):
    
    pelvis = [ q['pelvis_q0'], q['pelvis_q1'], q['pelvis_q2'], q['pelvis_q3']]
    
    thigh = [ q['upperLeg_q0'], q['upperLeg_q1'], q['upperLeg_q2'], q['upperLeg_q3']]
    
    q = quat_multiply(quat_conj(pelvis), thigh)
    
    t2 = 2*q[2]*q[3] - 2*q[0]*q[1]
    roll = -math.asin(t2)
    
    t0 = 2*q[1]*q[3] + 2*q[0]*q[2]
    t1 = 2*q[0]*q[0] - 1 + 2*q[3]*q[3]
    pitch = math.atan2(t0, t1)
    
    '''
    from sagemotion xyz
        t2 = 2.0*(qx*qz + qw*qy)
        t2 = 1.0 if t2 > 1.0 else t2 # correct if it is out of range
        t2 = -1.0 if t2 < -1.0 else t2 # correct if it is out of range
        pitch = math.asin(t2)
    '''

    t3 = 2*q[1]*q[2] + 2*q[0]*q[3]
    t4 = 2*q[0]*q[0] - 1 + 2*q[2]*q[2]
    yaw = math.atan2(t3, t4)
    
    
    # Convert to degrees
    roll = roll*180/np.pi
    pitch = pitch*180/np.pi
    yaw = yaw*180/np.pi
    
    return [roll, pitch, yaw]

'''
3 = x
2 = y
1 = z
ZXY = 132 <WRONG>
Quaternion to 132 or presumably ZXY euler from https://www.astro.rug.nl/software/kapteyn-beta/_downloads/attitude.pdf
'''
def astro132(data):
    
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
        
        q = quat_multiply(quat_conj(GS_pelvis_q),GS_thigh_q)
    
        t0 = -2*q[2]*q[3] + 2*q[0]*q[1]
        t1 = q[2]*q[2] - q[3]*q[3] + q[0]*q[0] - q[1]*q[1]
        roll = math.atan2(t0, t1)
    
        t2 = 2*q[1]*q[2] + 2*q[0]*q[3]
        pitch = math.asin(t2)
    
        t3 = -2*q[1]*q[3] + 2*q[0]*q[2]
        t4 = q[1]*q[1] + q[0]*q[0] - q[3]*q[3] - q[2]*q[2]
        yaw = math.atan2(t3, t4)
        
        
        # Convert to degrees
        roll = roll*180/np.pi
        pitch = pitch*180/np.pi
        yaw = yaw*180/np.pi
        
        return [roll, pitch, yaw]
    


# quaternion to ZYX euler from https://www.astro.rug.nl/software/kapteyn-beta/_downloads/attitude.pdf
def astro123(q):

        t0 = 2*q[2]*q[3] + 2*q[0]*q[1]
        t1 = q[3]*q[3] - q[2]*q[2] - q[1]*q[1] + q[0]*q[0]
        roll = math.atan2(t0, t1)
    
        t2 = 2*q[1]*q[3] - 2*q[0]*q[2]
        pitch = -math.asin(t2)
    
        t3 = 2*q[1]*q[2] + 2*q[0]*q[3]
        t4 = q[1]*q[1] + q[0]*q[0] - q[3]*q[3] - q[2]*q[2]
        yaw = math.atan2(t3, t4)
        
        
        # Convert to degrees
        roll = roll*180/np.pi
        pitch = pitch*180/np.pi
        yaw = yaw*180/np.pi
        
        return [roll, pitch, yaw]
    


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
    

# quaternion to XYZ euler from https://www.astro.rug.nl/software/kapteyn-beta/_downloads/attitude.pdf
def astro321(q):
    
        qw = q[0]
        qx = q[1]
        qy = q[2]
        qz = q[3]
    
        
        t0 = -2*q[1]*q[2] + 2*q[0]*q[3]
        t1 = q[1]*q[1] + q[0]*q[0] - q[3]*q[3] - q[2]*q[2]
        roll = math.atan2(t0, t1)
    
        t2 = 2*q[1]*q[3] + 2*q[0]*q[2]
        pitch = math.asin(t2)
    
        t3 = -2*q[2]*q[3] + 2*q[0]*q[1]
        t4 = q[3]*q[3] - q[2]*q[2] - q[1]*q[1] + q[0]*q[0]
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


    # Our code = math.asin ( 2 * (q_hipAngle.w * q_hipAngle.y - q_hipAngle.z * q_hipAngle.x) )
    
    t3 = 2.0*(-qy*qz + qw*qx)
    t4 = 1.0 - 2.0*(qx*qx + qy*qy)
    yaw = math.atan2(t3, t4)
    
    
    # Convert to degrees
    roll = roll*180/np.pi
    pitch = pitch*180/np.pi
    yaw = yaw*180/np.pi
    
    return [roll, pitch, yaw] 



def tbzyxOldEulerTBquat(q):
    
    t0 = 2*q[2]*q[3] + 2*q[0]*q[1]
    t1 = 2*q[0]*q[0] - 1 + 2*q[3]*q[3]
    roll = math.atan2(t0, t1)

    t2 = 2*q[1]*q[3] - 2*q[0]*q[2]
    pitch = -math.asin(t2)

    t3 = -2*q[1]*q[2] + 2*q[0]*q[3]
    t4 = 2*q[0]*q[0] - 1 + 2*q[1]*q[1]
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
    
    print(len(dataTypesNames))
    
    for i in range(len(dataTypesNames)) :
        
        print(dataTypesNames[i])
        ax.scatter(data[dataTypesNames[i]][columnNames[0]], data[dataTypesNames[i]][columnNames[1]], color=colors[i])
    
    ax.set_xlabel(xLabel)
    ax.set_ylabel(yLabel)
    ax.set_title(participantName + " " +  title)
    plt.axvline(x = (forwardEnd + backwardStart) / 2)
    plt.show()




'''
from XSENS AWINDA manual
MODIFIED TO DO LEFT AND RIGHT QUAT CALCS

'''
def XSENSquat2euler(q):
    
    pelvis = [ q['pelvis_q0'], q['pelvis_q1'], q['pelvis_q2'], q['pelvis_q3']]
    
    right_thigh = [ q['right_upperLeg_q0'], q['right_upperLeg_q1'], q['right_upperLeg_q2'], q['right_upperLeg_q3']]
    
    left_thigh = [ q['left_upperLeg_q0'], q['left_upperLeg_q1'], q['left_upperLeg_q2'], q['left_upperLeg_q3']]
    
    thigh = [right_thigh, left_thigh]
    
    result = [] # [ [right roll, pitch, yaw], [left roll, pitch, yaw] ]
    
    for i in range (0,2):
        
        q = quat_multiply(quat_conj(pelvis), thigh[i])
        
        # -R23
        t2 = 2*q[2]*q[3] - 2*q[0]*q[1]
        roll = -math.asin(t2)
        
        # Top = R13, Bottom = R33
        t0 = 2*q[1]*q[3] + 2*q[0]*q[2]
        t1 = 2*q[0]*q[0] + 2*q[3]*q[3] - 1
        pitch = math.atan2(t0, t1)
        
        # Top = R21, Bottom = R22
        t3 = 2*q[1]*q[2] + 2*q[0]*q[3]
        t4 = 2*q[0]*q[0] + 2*q[1]*q[1] - 1 
        yaw = math.atan2(t3, t4)
        
        
        # Convert to degrees
        roll = roll*180/np.pi
        pitch = pitch*180/np.pi
        yaw = yaw*180/np.pi
        
        result.append([roll, pitch, yaw])
    
    return result



'''
Should correspond to xsens ZXY
https://www.astro.rug.nl/software/kapteyn-beta/_downloads/attitude.pdf

'''
def astro213(q):
    
    t0 = -2*q[1]*q[3] + 2*q[0]*q[2]
    t1 = q[3]*q[3] - q[2]*q[2] - q[1]*q[1] + q[0]*q[0]
    roll = math.atan2(t0, t1)
    
    t2 = 2*q[2]*q[3] + 2*q[0]*q[1]
    pitch = math.asin(t2)
    
    t3 = -2*q[1]*q[2] + 2*q[0]*q[3]
    t4 = q[2]*q[2] - q[3]*q[3] + q[0]*q[0] - q[1]*q[1]
    yaw = math.atan2(t3, t4)
    
    
    # Convert to degrees
    roll = roll*180/np.pi
    pitch = pitch*180/np.pi
    yaw = yaw*180/np.pi
    
    return [roll, pitch, yaw]




def testHipAngle(participantName):
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
    
    # XSENS EXCEL FILES SETUP
 
    print("start getting excel")
    
    excel_quat_pelvis = getExcelQuaternions(trials[participantName][FILEPATH_INDEX], 'Segment Orientation - Quat', 1)

    print("got pelvis quat columns")
    
    
    # Right Upper Leg
    excel_quat_right_upperLeg = getExcelQuaternions(trials[participantName][FILEPATH_INDEX], 'Segment Orientation - Quat', 61)
    
    print("got RIGHT upper leg (thigh) quat columns")
    
    # XSENS RIGHT hip angle
    excel_hipZXY_right_flexion = pandas.read_excel(trials[participantName][FILEPATH_INDEX], 
                                             sheet_name='Joint Angles ZXY', 
                                             usecols=[45])
    
    print("got actual RIGHT hip angle columns")
    
    
    # Left Upper Leg
    excel_quat_left_upperLeg = getExcelQuaternions(trials[participantName][FILEPATH_INDEX], 'Segment Orientation - Quat', 77)

    print("got LEFT upper leg (thigh) quat columns")

    # XSENS LEFT LEG hip angle
    excel_hipZXY_left_flexion = pandas.read_excel(trials[participantName][FILEPATH_INDEX], 
                                             sheet_name='Joint Angles ZXY', 
                                             usecols=[57])

    print("got actual LEFT hip angle columns")
    
    #excel_shank_AccelZ = pandas.read_excel(trials[participantName][FILEPATH_INDEX], sheet_name='Segment Acceleration', usecols=[51])
    
    #print("got shank acceleration Z quat columns")
    
    row = trials[participantName][FORWARD_START_ROW]
    lastRow = trials[participantName][BACKWARD_END_ROW]

    # END SECTION --> XSENS EXCEL FILES SETUP
    
    
    
    hipData = { 'Right Calculated' : { 'Row' : [], 'Joint Angle' : [] },
                'Right Actual' : { 'Row' : [], 'Joint Angle' : [] },
                'Left Calculated' : { 'Row' : [], 'Joint Angle' : [] },
                'Left Actual' : { 'Row' : [], 'Joint Angle' : [] },
                'Crossed Threshold' : { 'Row' : [], 'Joint Angle' : [] },
               }
    
    
    while(row < lastRow):
        
        data = {
                    'pelvis_q0': excel_quat_pelvis[0]['Pelvis q0'].iloc[row],
                    'pelvis_q1': excel_quat_pelvis[1]['Pelvis q1'].iloc[row],
                    'pelvis_q2': excel_quat_pelvis[2]['Pelvis q2'].iloc[row],
                    'pelvis_q3': excel_quat_pelvis[3]['Pelvis q3'].iloc[row],
                    
                    'right_upperLeg_q0': excel_quat_right_upperLeg[0]['Right Upper Leg q0'].iloc[row],
                    'right_upperLeg_q1': excel_quat_right_upperLeg[1]['Right Upper Leg q1'].iloc[row],
                    'right_upperLeg_q2': excel_quat_right_upperLeg[2]['Right Upper Leg q2'].iloc[row],
                    'right_upperLeg_q3': excel_quat_right_upperLeg[3]['Right Upper Leg q3'].iloc[row],
                    
                    'left_upperLeg_q0': excel_quat_left_upperLeg[0]['Left Upper Leg q0'].iloc[row],
                    'left_upperLeg_q1': excel_quat_left_upperLeg[1]['Left Upper Leg q1'].iloc[row],
                    'left_upperLeg_q2': excel_quat_left_upperLeg[2]['Left Upper Leg q2'].iloc[row],
                    'left_upperLeg_q3': excel_quat_left_upperLeg[3]['Left Upper Leg q3'].iloc[row],
                    
                    }
    
        rightActualHip = excel_hipZXY_right_flexion['Right Hip Flexion/Extension'].iloc[row]
        leftActualHip = excel_hipZXY_left_flexion['Left Hip Flexion/Extension'].iloc[row]
        
        addData(hipData, 'Right Actual', [row, rightActualHip])
        addData(hipData, 'Left Actual', [row, leftActualHip])
        
        # XSENSquat2euler returns [ [right roll, pitch, yaw], [left roll, pitch, yaw] ]
        eulerAngles = XSENSquat2euler(data) 
        rightHipAngle = -eulerAngles[0][1]
        leftHipAngle = -eulerAngles[1][1]
        
        addData(hipData, 'Right Calculated', [row, rightHipAngle])
        addData(hipData, 'Left Calculated', [row, leftHipAngle])
        
        row += 1
    
    
    
    ## START GRAPHING
    
    rightKeys = ['Right Calculated', 'Right Actual']
    leftKeys = ['Left Calculated', 'Left Actual']
    colors = ['g','b']
    
    startRow = trials[participantName][FORWARD_END_ROW]
    endRow = trials[participantName][BACKWARD_START_ROW]
    
    graph(hipData, startRow, endRow,
            participantName, 'RIGHT Hip Calculations (-pitch))',
            'Row', 'Hip Flexion/Extension', 
            rightKeys, ['Row', 'Joint Angle'], colors)
    
    graph(hipData, startRow, endRow,
            participantName, 'LEFT Hip Calculations (-pitch))',
            'Row', 'Hip Flexion/Extension', 
            leftKeys, ['Row', 'Joint Angle'], colors)
    


def main():
    
    
    
    sageMotionData = '/Users/shana/Desktop/DesktopItems/BIOFEEDBACK/SageMotionSupport20210402/hip joint trial16.xlsx'
        
    print("start getting excel")
    
    sheetName = 'Sheet1'
    
    excel_quat_pelvis = getExcelQuaternions(sageMotionData, sheetName, 44)
    
    print("got pelvis quat columns")
    
    # Right Upper Leg
    excel_quat_upperLeg = getExcelQuaternions(sageMotionData, sheetName, 28)
    
    
    row = 0
    lastRow = 5
    
    while(row < lastRow):
        
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
    
        pelvis_quat = pyq.Quaternion(data['pelvis_q0'],data['pelvis_q1'],data['pelvis_q2'],data['pelvis_q3'])
        upperLeg_quat = pyq.Quaternion(data['upperLeg_q0'],data['upperLeg_q1'],data['upperLeg_q2'],data['upperLeg_q3'])
        
        pelvis_sage_quat = [data['pelvis_q0'],data['pelvis_q1'],data['pelvis_q2'],data['pelvis_q3']]
        upperLeg_sage_quat = [data['upperLeg_q0'],data['upperLeg_q1'],data['upperLeg_q2'],data['upperLeg_q3']]
        
        print("~~~~~~~~~~~~~~~~~~ ROW ", row, "~~~~~~~~~~~~~~~~~~")
        
        print("func quat = ", pelvis_quat)
        print("SAGE quat = ", pelvis_sage_quat)
        
        print("\n")
        
        # These are the same
        # print("func conjugate = ", pelvis_quat.conjugate)
        # print("SAGE conjugate = ", quat_conj(pelvis_sage_quat))
        
        #print("\n")
        
        # These are the same
        #print("func multiplication = ", pelvis_quat.conjugate * upperLeg_quat)
        #print("SAGE multiplication = ", quat_multiply( quat_conj(pelvis_sage_quat), upperLeg_sage_quat) )
        
        #print("\n")
              
        # func theta = SAGE regular quat to euler second element
        #print("func quat to euler = ", math.atan2( 2 * (pelvis_quat.w * pelvis_quat.x + pelvis_quat.y * pelvis_quat.z), 1 - 2 * (pelvis_quat.x**2 + pelvis_quat.y**2) ) * 180/math.pi, ", ",
              #math.asin( 2 * (pelvis_quat.w * pelvis_quat.y - pelvis_quat.z * pelvis_quat.x) ) * 180/math.pi, ", ",
              #math.atan2( 2 * (pelvis_quat.w * pelvis_quat.z + pelvis_quat.x * pelvis_quat.y), 1 - 2 * (pelvis_quat.y**2 + pelvis_quat.z**2) ) * 180/math.pi )
        '''print("SAGE quat to euler XYZ = ", quat2eulerXYZ(pelvis_sage_quat))
        print('ASTRO quat to euler 321 = ', astro321(pelvis_sage_quat))
        
        print('\n')
        
        #eng = matlab.engine.start_matlab()
        #print(eng.quat2eul(pelvis_sage_quat,'ZXY'))
        
        print('\n')
        
        print("SAGE quat to euler ZYX = ", quat2euler(pelvis_sage_quat))
        print('ASTRO quat to euler 123 = ', astro123(pelvis_sage_quat))
        
        print('\n')'''
        
        print("XSENS calculated ZXY = ", XSENSquat2euler(pelvis_sage_quat))
        print('ASTRO 213 = ', astro213(pelvis_sage_quat))
        
        print("\n\n")
        
        row += 1
        
    



if __name__ == "__main__":
    
    #main()
    
    testHipAngle('p401')
    
    
    
    
