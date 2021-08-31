import main
import sageMotionFunctions


'''
HS: (1) find negative minima in shank ang velY
(2) find positive maxima for shank ang velX
(3) find postive maxima for shank ang velY
(4) let shank ang velY be positive for 300ms
(5) if 5 HS are found, then set the average values as the tresholding, then do steps #1, #3, and #4
- adds shank ang vel y, not shank accel z

NOTE:
- HS rows for these would be 300ms after the HS event
'''
def getGaitEventsWithThresholdAnd300MSPositive(self):

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

            self.foundNegMinima = False
            self.foundPosMaxima = False
            
            HSstartRow = self.row

            shankAngVelYPositive = True

            # check if shankAngVelY is positive for 300 ms
            while ( shankAngVelYPositive 
                and self.row - HSstartRow < main.convertMilliSecToRow(self.frequency, 300) 
                and self.row < self.lastRow ) :
                
                self.row += 1
                main.getData(self)
                main.setPreviousData(self)

                if ( self.shankAngVelY < 0 ):
                    shankAngVelYPositive = False

            # if shankAngVelY stayed positive for 300 ms, then add HS event
            if shankAngVelYPositive :

                self.gaitData['HS']['Row'].append(self.row)
                self.gaitData['HS']['Shank Ang Vel Y'].append(self.previousShankAngVelY)

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




'''
HS: (1) find negative minima in shank ang velY
(2) find positive maxima for shank ang velX
(3) find postive maxima for shank ang velY
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



'''
HS: (1) find negative minima in shank ang velY
(2) find positive maxima for shank ang velX
(3) find postivie maxima for shank ang velY
(4) wait 300 ms before looking for the next HS
'''
def getGaitEvents(self):
    # If negative minima is found,
    # then first positive maxima is HS
    
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
        self.gaitData['HS']['Shank Accel Z'].append(self.shankAccelZ)
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




def sageMotionGaitDetection(self):
# Update the current gait phase

    # Heel strike event algorithm based on:
    # Yun2012, Estimation of Human Foot Motion During Normal Walking Using Inertial..., Section IIC
    # heel strike event occurs when magnitude of gyroscope drops below 45 deg/s for at least xxx ms
    # 45 deg/s value selected based on Wisit's code and Haisheng testing (Junkai told me this 2019-06-19)


    # :+) QUESTIONS:
    # :+) - gyroscope for what body part? [foot]
    # :+) - seems like it's time based, not actual data initiating the heel strike event (for early stance, late stance, swing)



    # Set threshold values
    THRESH_GYROMAG_HEELSTRIKE = 45 # (deg/s)
    THRESH_GYROMAG_TOEOFF = 45 # (deg/s)

    THRESH_ITERS_CONSECUTIVE_BELOW_THRESH_GYROMAG_HEELSTRIKE = 0.1*self.DATARATE # 0.1 s, consecutitive iterations below the gyro mag threshold value for heelstrike
    THRESH_ITERS_CONSECUTIVE_ABOVE_THRESH_GYROMAG_TOEOFF = 0.1*self.DATARATE # 0.1 s, consecutitive iterations above the gyro mag threshold value for toeoff

    THRESH_ITERS_TO_STANCE_LATE = self.stancetime*0.5*self.DATARATE # 50% of stance time

    # Compute gyroscope magnitude
    GyroX = self.data['footAngVelX']
    GyroY = self.data['footAngVelY']
    GyroZ = self.data['footAngVelZ']
    gyroMag = sageMotionFunctions.mag([GyroX,GyroY,GyroZ])
    # print("gyro mag: {:.1f}  gaitphase: {}".format(gyroMag,self.gaitphase))

    gaitphase_old = self.gaitphase

    print(gaitphase_old, ', ', gyroMag)

    # SWING PHASE
    if gaitphase_old == 'swing':
        # :+) increase iterations below threshold
        if gyroMag < THRESH_GYROMAG_HEELSTRIKE:
            print('HEEL STRIKE BELOWWWWWW THRESH')
            self.iters_consecutive_below_thresh_gyroMag_heelstrike += 1
        # :+) reset number of  iterations below threshold
        else:
            print('HEEL STRIKE ABOVE THRESH')
            self.iters_consecutive_below_thresh_gyroMag_heelstrike = 0

        # :+) if number of iterations below threshold exceeds the threshold time, then it's a HS; 
        # :+) reset iterations below threshold and set gaitphase to early stance
        if self.iters_consecutive_below_thresh_gyroMag_heelstrike > THRESH_ITERS_CONSECUTIVE_BELOW_THRESH_GYROMAG_HEELSTRIKE:
            # Heel strike event detected

            self.gaitData['HS']['Row'].append(self.row)
            self.gaitData['HS']['Shank Ang Vel Y'].append(self.previousShankAngVelY)

            self.iters_since_last_heelstrike = 0
            self.iters_consecutive_below_thresh_gyroMag_heelstrike = 0
            self.gaitphase = 'stance_early'

    # STANCE EARLY PHASE
    elif gaitphase_old == 'stance_early':
        if self.iters_since_last_heelstrike > THRESH_ITERS_TO_STANCE_LATE:
            print('WAIT FINISHED')
            self.gaitphase = 'stance_late'

    # STANCE LATE PHASE
    elif gaitphase_old == 'stance_late':
        if gyroMag > THRESH_GYROMAG_TOEOFF:
            print('TOE OFF ABOVE THRESH')
            self.iters_consecutive_above_thresh_gyroMag_toeoff += 1
        else:
            print('TOE OFF BELOWWW THRESH TOEOFF')
            self.iters_consecutive_above_thresh_gyroMag_toeoff = 0

        if self.iters_consecutive_above_thresh_gyroMag_toeoff > THRESH_ITERS_CONSECUTIVE_ABOVE_THRESH_GYROMAG_TOEOFF:
            # Toe-off event detected
            self.iters_consecutive_above_thresh_gyroMag_toeoff = 0
            self.gaitphase = 'swing'


    self.iters_since_last_heelstrike += 1



