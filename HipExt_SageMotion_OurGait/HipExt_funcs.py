import numpy as np
import math

def update_gaitphase(self,node_num,data):
# Update the current gait phase

    # Heel strike event algorithm based on:
    # Yun2012, Estimation of Human Foot Motion During Normal Walking Using Inertial..., Section IIC
    # heel strike event occurs when magnitude of gyroscope drops below 45 deg/s for at least xxx ms
    # 45 deg/s value selected based on Wisit's code and Haisheng testing (Junkai told me this 2019-06-19)

    # Set threshold values
    THRESH_GYROMAG_HEELSTRIKE = 45 # (deg/s)
    THRESH_GYROMAG_TOEOFF = 45 # (deg/s)

    THRESH_ITERS_CONSECUTIVE_BELOW_THRESH_GYROMAG_HEELSTRIKE = 0.1*self.DATARATE # 0.1 s, consecutitive iterations below the gyro mag threshold value for heelstrike
    THRESH_ITERS_CONSECUTIVE_ABOVE_THRESH_GYROMAG_TOEOFF = 0.1*self.DATARATE # 0.1 s, consecutitive iterations above the gyro mag threshold value for toeoff

    THRESH_ITERS_TO_STANCE_LATE = self.stancetime*0.5*self.DATARATE # 50% of stance time

    # Compute gyroscope magnitude
    GyroX = data[node_num]['GyroX']; GyroY = data[node_num]['GyroY']; GyroZ = data[node_num]['GyroZ']
    gyroMag = mag([GyroX,GyroY,GyroZ])
    # print("gyro mag: {:.1f}  gaitphase: {}".format(gyroMag,self.gaitphase))

    gaitphase_old = self.gaitphase

    # SWING PHASE
    if gaitphase_old == 'swing':
        if gyroMag < THRESH_GYROMAG_HEELSTRIKE:
            self.iters_consecutive_below_thresh_gyroMag_heelstrike += 1
        else:
            self.iters_consecutive_below_thresh_gyroMag_heelstrike = 0

        if self.iters_consecutive_below_thresh_gyroMag_heelstrike > THRESH_ITERS_CONSECUTIVE_BELOW_THRESH_GYROMAG_HEELSTRIKE:
            # Heel strike event detected
            self.iters_since_last_heelstrike = 0
            self.iters_consecutive_below_thresh_gyroMag_heelstrike = 0
            self.gaitphase = 'stance_early'

    # STANCE EARLY PHASE
    elif gaitphase_old == 'stance_early':
        if self.iters_since_last_heelstrike > THRESH_ITERS_TO_STANCE_LATE:
            self.gaitphase = 'stance_late'

    # STANCE LATE PHASE
    elif gaitphase_old == 'stance_late':
        if gyroMag > THRESH_GYROMAG_TOEOFF:
            self.iters_consecutive_above_thresh_gyroMag_toeoff += 1
        else:
            self.iters_consecutive_above_thresh_gyroMag_toeoff = 0

        if self.iters_consecutive_above_thresh_gyroMag_toeoff > THRESH_ITERS_CONSECUTIVE_ABOVE_THRESH_GYROMAG_TOEOFF:
            # Toe-off event detected
            self.iters_consecutive_above_thresh_gyroMag_toeoff = 0
            self.gaitphase = 'swing'


    self.iters_since_last_heelstrike += 1









'''
Our Gait detection algorithm from ../gaitAlgorithms.py

HS: (1) find negative minima in shank ang velY
(2) find positive maxima for shank ang velX
(3) find positive maxima for shank ang velY
(4) wait 300 ms before looking for the next HS

DIFF FROM GETgaitEVENTS()
(5) if 5 HS are found, then set the average values as the tresholding, then do steps #1, #3, and #4
- adds shank ang vel y, not shank accel z
'''
def getGaitEventsWithThreshold(self):

    # If there are 5 HS events are already found, use 70% of the average to be the threshold to find the next positive maxima in ang velY
    if( len(self.gaitData['HS']['Shank Ang Vel Y']) > 5 ):
        if ( len(self.gaitData['HS']['Shank Ang Vel Y']) == 6 ) :
            subArray = self.gaitData['HS']['Shank Ang Vel Y'][:5]
            self.averageMax = sum(subArray)/5
            # print("ANG VEL Y VALUES = ", self.gaitData['HS']['Row'])
            # print("ANG VEL Y VALUES = ", self.gaitData['HS']['Shank Ang Vel Y'])
            # print("AVERAGE MAX = ", self.averageMax)

        # negative minima
        if ( not self.foundNegMinima 
            and self.previousShankAngVelYDifference < 0 
            and self.shankAngVelYDifference > 0 
            and self.previousShankAngVelY < 0 ) :
            self.foundNegMinima = True


        # positive maxima
        if ( self.foundNegMinima
            and self.previousShankAngVelYDifference > 0 
            and self.shankAngVelYDifference < 0 
            and self.previousShankAngVelY > self.averageMax) :

            self.gaitData['HS']['Row'].append(self.row)
            self.gaitData['HS']['Shank Ang Vel Y'].append(self.previousShankAngVelY)
            self.foundNegMinima = False
            self.foundPosMaxima = False
            
            HSstartRow = self.row

            while ( self.row - HSstartRow < main.convertMilliSecToRow(self.frequency, 300) 
                and self.row < self.lastRow ) :
                
                self.row += 1
                main.getData(self)
                main.setPreviousData(self)

        else:

            main.setPreviousData(self)
    
    else:
        
        # negative minima
        if ( not self.foundNegMinima 
            and self.previousShankAngVelYDifference < 0 
            and self.shankAngVelYDifference > 0 
            and self.previousShankAngVelY < 0 ) :
            self.foundNegMinima = True
            
        # positive maxima for shank ang vel X
        if ( not self.foundPosMaxima 
            and self.previousShankAngVelXDifference > 0 
            and self.shankAngVelXDifference < 0 
            and self.previousShankAngVelX > 0 ) :
            self.foundPosMaxima = True
        
        # positive maxima
        if ( self.foundNegMinima 
            and self.foundPosMaxima 
            and self.previousShankAngVelYDifference > 0 
            and self.shankAngVelYDifference < 0 
            and self.previousShankAngVelY > 0 ) :

            self.gaitData['HS']['Row'].append(self.row)
            self.gaitData['HS']['Shank Ang Vel Y'].append(self.shankAngVelY)
            self.foundNegMinima = False
            self.foundPosMaxima = False
            
            HSstartRow = self.row
            
            
            while ( self.row - HSstartRow < main.convertMilliSecToRow(self.frequency, 300) 
                and self.row < self.lastRow ) :
                
                self.row += 1
                main.getData(self)
                main.setPreviousData(self)

        else:

            main.setPreviousData(self)
















# Sensor to segment calibration.
def calibrate(self, data):

    # Find GS_q_init
    self.GS_pelvis_q_init = [
                    data[self.NodeNum_pelvis]['Quat1'],
                    data[self.NodeNum_pelvis]['Quat2'],
                    data[self.NodeNum_pelvis]['Quat3'],
                    data[self.NodeNum_pelvis]['Quat4']]
    self.GS_thigh_q_init = [
                    data[self.NodeNum_thigh]['Quat1'],
                    data[self.NodeNum_thigh]['Quat2'],
                    data[self.NodeNum_thigh]['Quat3'],
                    data[self.NodeNum_thigh]['Quat4']]
    # self.GS_foot_q_init = [
                    # data[self.NodeNum_foot]['Quat1'],
                    # data[self.NodeNum_foot]['Quat2'],
                    # data[self.NodeNum_foot]['Quat3'],
                    # data[self.NodeNum_foot]['Quat4']]

    GS_pelvis_q0 = self.GS_pelvis_q_init
    GS_thigh_q0 = self.GS_thigh_q_init


    pelvis_Euler = quat2euler(GS_pelvis_q0)
    thigh_Euler = quat2euler(GS_thigh_q0)
    # pelvis IMU is the reference IMU.
    if self.config['whichLeg'] == "Right Leg":
        TmpPoseRef = [0,0,-((thigh_Euler[2]-90)-pelvis_Euler[2])]
        self.thigh_Yawoffset_q = euler2quat(TmpPoseRef)
    else:
        TmpPoseRef = [0,0,-((thigh_Euler[2]+90)-pelvis_Euler[2])]
        self.thigh_Yawoffset_q = euler2quat(TmpPoseRef)

    pelvis_init_Yaw = pelvis_Euler[2]
    # commonYaw is pelvis_init_Yaw
    # for pelvis IMU calibrate
    GB_Euler0_target = [0,0,pelvis_init_Yaw]  # this is our alignment target, we expect rotate IMU to this orientation, both pelvis and thigh have the same target.
    GB_q0_target = euler2quat(GB_Euler0_target)  # target in quaternion format.
    GS_q0 = GS_pelvis_q0  # current IMU orientation, in global coordinate.
    self.BS_q_pelvis_inv = quat_multiply(quat_conj(GS_q0),GB_q0_target)  # conjugate quaternion of thigh sensor to segment quaternion. inv represent for inversion, the same as conjugate.
    # refer to Hip angle tutorial SageMotion.pptx step2.

    if self.config['whichLeg'] == "Right Leg":
        R_thigh_init_Yaw = thigh_Euler[2]-90
    else:
        R_thigh_init_Yaw = thigh_Euler[2]+90
    if R_thigh_init_Yaw > 180:
        R_thigh_init_Yaw = R_thigh_init_Yaw - 360
    elif R_thigh_init_Yaw < -180:
        R_thigh_init_Yaw = R_thigh_init_Yaw + 360

    # for thigh IMU calibrate
    GB_Euler0_target = [0,0,R_thigh_init_Yaw]  # this is our alignment target, we expect rotate IMU to this orientation, both pelvis and thigh have the same target.
    GB_q0_target = euler2quat(GB_Euler0_target)  # target in quaternion format.
    GS_q0 = GS_thigh_q0  # current IMU orientation, in global coordinate.
    self.BS_q_thigh_inv = quat_multiply(quat_conj(GS_q0),GB_q0_target)

    print("Hip angle Calibrate finished")


# Calculate Hip Knee Ankle angle, only in sagittal
def calculate_HipExtAngle(self, data):

#     print("calculate_HipExtAngle")
    GS_pelvis_q = [
                    data[self.NodeNum_pelvis]['Quat1'],
                    data[self.NodeNum_pelvis]['Quat2'],
                    data[self.NodeNum_pelvis]['Quat3'],
                    data[self.NodeNum_pelvis]['Quat4']]
    GS_thigh_q = [
                    data[self.NodeNum_thigh]['Quat1'],
                    data[self.NodeNum_thigh]['Quat2'],
                    data[self.NodeNum_thigh]['Quat3'],
                    data[self.NodeNum_thigh]['Quat4']]

    GS_q = GS_pelvis_q
    BS_q = self.BS_q_pelvis_inv
    GB_pelvis_q = quat_multiply(GS_q,BS_q)


    GS_q = GS_thigh_q
    BS_q = self.BS_q_thigh_inv
    GB_thigh_q = quat_multiply(GS_q,BS_q)
    GB_thigh_q = quat_multiply(self.thigh_Yawoffset_q,GB_thigh_q) # Yaw correction

    # calculate three dimensional hip angles
    B_q_hip_angles = quat_multiply(quat_conj(GB_pelvis_q),GB_thigh_q)

    this_Euler = quat2eulerXYZ(B_q_hip_angles)  # Euler must be XYZ order, which is the same as the definition of hip angle.

    Hip_rot = this_Euler[0]   # hip internal rotation.
    Hip_abd = this_Euler[1]   # hip abduction angle.
    Hip_ext = this_Euler[2]  # hip flexion angle.

    # Test print
    if self.iteration % 100 == 0:
        print("hip angle [roll(X) pitch(Y) yaw(Z)]")
        print(np.around(this_Euler,decimals=3))
        print("")


    return (Hip_ext,Hip_abd,Hip_rot)


def give_feedback(self):

    angleVal = self.Hip_ext
    if angleVal < self.MIN_THRESHOLD:
        self.my_sage.feedback_on(self.NodeNum_feedback_min, self.info["pulse_length"])
        self.feedback_min = 1
        self.feedback_max = 0
    elif angleVal > self.MAX_THRESHOLD:
        self.my_sage.feedback_on(self.NodeNum_feedback_max, self.info["pulse_length"])
        self.feedback_min = 0
        self.feedback_max = 1
    else:
        self.feedback_min = 0
        self.feedback_max = 0

    self.alreadyGivenFeedback = 1

    # print("give_feedback, fan testing add euler output")
    # print('%d' %self.iteration)


def mag(x):
    return math.sqrt(sum(i**2 for i in x))


def quat_multiply(a, b):
    c = []
    c.append(a[0]*b[0]-a[1]*b[1]-a[2]*b[2]-a[3]*b[3])
    c.append(a[0]*b[1]+a[1]*b[0]+a[2]*b[3]-a[3]*b[2])
    c.append(a[0]*b[2]+a[2]*b[0]+a[3]*b[1]-a[1]*b[3])
    c.append(a[0]*b[3]+a[3]*b[0]+a[1]*b[2]-a[2]*b[1])
    return c


def quat_conj(a):
    return [a[0], -a[1], -a[2], -a[3]]


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

    # if self.iteration % 100 == 0:
        # qw = data[self.NodeNum_foot]['Quat1']
        # qx = data[self.NodeNum_foot]['Quat2']
        # qy = data[self.NodeNum_foot]['Quat3']
        # qz = data[self.NodeNum_foot]['Quat4']
        # this_Euler = quat2euler([qw,qx,qy,qz])
        # print("sensor foot [roll(X) pitch(Y) yaw(Z)]")
        # print(np.around(this_Euler,decimals=3))
        # print("")
