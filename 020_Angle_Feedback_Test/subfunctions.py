import numpy as np
import math

# Calculate the Sensor Sway Angle for the current time
def calculate_angle(node_num,data):

    # Get quaternions
    qw = data[node_num]['Quat1']
    qx = data[node_num]['Quat2']
    qy = data[node_num]['Quat3']
    qz = data[node_num]['Quat4']

    # Convert quaternions to Euler angles
    # bediyap.com/programming/convert-quaternion-to-euler-rotations/

    # case zyz, Rotation sequence: Z->Y->Z
    t0 = 2*(qy*qz + qw*qx)
    t1 = -2*(qx*qz - qw*qy)

    roll = np.arctan2(t0, t1) # in radians
    roll = roll*180/3.14159 - 90 # in deg and adjusted for keeping the sensor vertical

#    this_angle is corresponding to the sway angle when the sensor is kept vertical with switch pointing up
    this_angle = roll

    return this_angle



'''


*** ANGLE CALCULATION *** 


'''

def calibrate(data):

    # Sample fetching quaternions format:
    # qw = data[node_num]['Quat1']
    # qx = data[node_num]['Quat2']
    # qy = data[node_num]['Quat3']
    # qz = data[node_num]['Quat4']

    # Assuming pelvis node_num is 0
    GS_pelvis_q_init = [
                    data[0]['Quat1'],
                    data[0]['Quat2'],
                    data[0]['Quat3'],
                    data[0]['Quat4'],
                    ]
    # Assuming thigh node_num is 1
    GS_thigh_q_init = [
                    data[1]['Quat1'],
                    data[1]['Quat2'],
                    data[1]['Quat3'],
                    data[1]['Quat4'],
                    ]
    
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



def calculate_HipExtAngle(data, BS_q_pelvis_inv, BS_q_thigh_inv)
    
    # Assuming pelvis node_num is 0
    GS_pelvis_q = [
                    data[0]['Quat1'],
                    data[0]['Quat2'],
                    data[0]['Quat3'],
                    data[0]['Quat4'],
    # Assuming thigh node_num is 1
    GS_thigh_q = [
                    data[1]['Quat1'],
                    data[1]['Quat2'],
                    data[1]['Quat3'],
                    data[1]['Quat4'],
                ]
    
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
    
    return (Hip_flex,Hip_abd,Hip_rot)



'''

*** QUATERNION HELPERS ***


'''


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

