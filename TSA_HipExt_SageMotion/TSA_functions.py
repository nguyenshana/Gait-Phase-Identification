import numpy as np
import math

# Determine the current gait phase
def get_gaitphase(gaitphase_old,stancetime,iters_consecutive_below_gyroMag_thresh,\
                  iters_since_last_heelstrike,node_num,data,UPDATE_RATE):

# Heel strike event algorithm based on:
# Yun2012, Estimation of Human Foot Motion During Normal Walking Using Inertial..., Section IIC
# heel strike event occurs when magnitude of gyroscope drops below 0.2 for at least xxx ms
# 0.2 value selected based on Junkai's testing 2019.6.23

    # Set threshold values
#    UPDATE_RATE = 50 #Hz
    THRESH_GYROMAG_ITERS = 5
    THRESH_GYROMAG_LO = 45
    THRESH_GYROMAG_HI = 150
    THRESH_ITERS_TO_STANCE_MID = stancetime*0.2*UPDATE_RATE
    THRESH_ITERS_TO_STANCE_LATE = stancetime*0.5*UPDATE_RATE
    THRESH_ITERS_TO_SWING = stancetime*UPDATE_RATE


    gaitphase = gaitphase_old

    GyroX = data[node_num]['GyroX']
    GyroY = data[node_num]['GyroY']
    GyroZ = data[node_num]['GyroZ']
    gyroMag = mag([GyroX,GyroY,GyroZ])
    #print("gyro mag: {:.1f}  thresh: {}".format(gyroMag,THRESH_GYROMAG_LO))

    # SWING PHASE
    if gaitphase_old == 'swing':

        if gyroMag < THRESH_GYROMAG_LO:
            iters_consecutive_below_gyroMag_thresh += 1
        else:
            iters_consecutive_below_gyroMag_thresh = 0

        if iters_consecutive_below_gyroMag_thresh > THRESH_GYROMAG_ITERS:
            iters_since_last_heelstrike = 0
            iters_consecutive_below_gyroMag_thresh = 0
            gaitphase = 'stance_early'

    # STANCE EARLY PHASE
    elif gaitphase_old == 'stance_early':
        if iters_since_last_heelstrike > THRESH_ITERS_TO_STANCE_MID:
            gaitphase = 'stance_mid'

    # STANCE MID PHASE
    elif gaitphase_old == 'stance_mid':
        if iters_since_last_heelstrike > THRESH_ITERS_TO_STANCE_LATE:
            gaitphase = 'stance_late'

    # STANCE LATE PHASE
    elif gaitphase_old == 'stance_late':
        if iters_since_last_heelstrike > THRESH_ITERS_TO_SWING and gyroMag > THRESH_GYROMAG_HI:
            gaitphase = 'swing'


    iters_since_last_heelstrike += 1

    return (gaitphase,iters_consecutive_below_gyroMag_thresh,iters_since_last_heelstrike)


# Get current step number
def get_stepnum(gaitphase_last,gaitphase_this,stepnum):

    if gaitphase_last == 'swing' and gaitphase_this == 'stance_early':
        stepnum += 1

    return (stepnum)


# Get current stride time
def get_stridetime(gaitphase_last,gaitphase_this,UPDATE_RATE,timesteps_since_last_heelstrike,stridetime):

    if gaitphase_last == 'swing' and gaitphase_this == 'stance_early':
        stridetime = timesteps_since_last_heelstrike / UPDATE_RATE #seconds

    return (stridetime)


# Calculate TSA min and max for last step
def get_TSA_min_max_last_step(gaitphase_last,gaitphase_this,TSA_array,TSA_min,TSA_max):

    if gaitphase_last == 'swing' and gaitphase_this == 'stance_early':
        TSA_min = min(TSA_array)
        TSA_max = max(TSA_array)
        TSA_array = []

    return (TSA_min,TSA_max,TSA_array)


# Calculate the Trunk Sway Angle for the current time step
def calculate_TSA(node_num,data):

    # Get quaternions
    qw = data[node_num]['Quat1']
    qx = data[node_num]['Quat2']
    qy = data[node_num]['Quat3']
    qz = data[node_num]['Quat4']


    # Convert quaternions to Euler angles
    # bediyap.com/programming/convert-quaternion-to-euler-rotations/

    # case zyz, Rotation sequence: Z->Y->Z, this works best
    t0 = 2*(qy*qz + qw*qx)
    t1 = -2*(qx*qz - qw*qy)

    # case zyx, Rotation sequence: X->Y->Z
#    t0 = 2*(qy*qz + qw*qx)
#    t1 = qw*qw - qx*qx - qy*qy + qz*qz

    # case xyz, Rotation sequence: Z->Y->X
#    t0 = -2*(qx*qy - qw*qz)
#    t1 = qw*qw + qx*qx - qy*qy - qz*qz

    roll = np.arctan2(t0, t1) # in radians
    roll = roll*180/3.14159 - 90 # in deg and adjusted for attaching to the back

#    TSA = data[0]['AccelZ']
    TSA = roll

    return TSA


# Print out the x,y,z acceromater values to test the labeled node axes
def test_node_axes_directions(node_num, data):

    x = data[node_num]['AccelX']
    y = data[node_num]['AccelY']
    z = data[node_num]['AccelZ']

    #print("Node [{}] (Accel X,Y,Z): {:.2f} {:.2f} {:.2f}".format(node_num,x,y,z))


def mag(x):
    return math.sqrt(sum(i**2 for i in x))
