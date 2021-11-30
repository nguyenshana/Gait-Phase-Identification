import time
import numpy as np
from sage.base_app import BaseApp
if __name__ == '__main__':
    import HipExt_funcs
else:
    from .import HipExt_funcs


class Core(BaseApp):
###########################################################
# INITIALIZE APP

# Comments formatted as:

'''
** NOTE **
'''

# were added by Shana/not Sagemotion
###########################################################
    def __init__(self, my_sage):
        BaseApp.__init__(self, my_sage, __file__)

        self.gaitphase = 'swing' # default gait phase
        self.stridetime = 1.0
        self.stancetime = 0.6*self.stridetime

        self.DATARATE = self.info["datarate"]
        self.MIN_THRESHOLD = float(self.config['min_threshold'])
        self.MAX_THRESHOLD = float(self.config['max_threshold'])
        self.FEEDBACK_DELAY = float(self.config['feedback_delay'])

        # self.NodeNum_foot = self.info["sensors"].index('foot')
        self.NodeNum_thigh = self.info["sensors"].index('thigh')
        self.NodeNum_pelvis = self.info["sensors"].index('pelvis')
        self.NodeNum_feedback_min = self.info["feedback"].index('feedback_min')
        self.NodeNum_feedback_max = self.info["feedback"].index('feedback_max')

        self.iteration = 0
        self.iters_consecutive_below_thresh_gyroMag_heelstrike = 0
        self.iters_consecutive_above_thresh_gyroMag_toeoff = 0
        self.iters_since_last_heelstrike = 0

        self.feedback_min = 0
        self.feedback_max = 0

        self.alreadyGivenFeedback = 0
        self.thigh_Yawoffset_q = [1,0,0,0]

        self.BS_q_pelvis_inv = [1,0,0,0]  # sensor to segment alignment quaternion, inv denotes conjugate.
        self.BS_q_thigh_inv = [1,0,0,0]


###########################################################
# CHECK NODE CONNECTIONS
###########################################################
    # Check if nodes are connected properly
    def check_status(self):
        sensors_count = self.get_sensors_count()
        feedback_count = self.get_feedback_count()
        err_msg = ""
        if sensors_count < len(self.info['sensors']):
            err_msg += "App requires {} sensor nodes but only {} are connected".format(
                    len(self.info['sensors']), sensors_count)
        if feedback_count < len(self.info['feedback']):
            err_msg += "App require {} feedback nodes but only {} are connected".format(
                    len(self.info['feedback']), feedback_count)
        if err_msg != "":
            return False, err_msg
        return True, "Now running App"


###########################################################
# RUN APP IN LOOP
###########################################################
    def run_in_loop(self):
        data = self.my_sage.get_next_data()
        self.iteration += 1

        # Test print sensor quaternions
        HipExt_funcs.test_print_sensor_quaternions(self,data)

        # Calibrate to find BS_q, sensor to body segment alignment quaternions on 1st iteration
        if self.iteration == 1:
            HipExt_funcs.calibrate(self,data) #

        # Find the gait phase

        '''
        ** ORIGINALLY COMMENTED OUT **
        '''
        HipExt_funcs.update_gaitphase(self,self.NodeNum_foot,data)

        # Calculate hip extension angle
        (Hip_ext,Hip_abd,Hip_rot) = HipExt_funcs.calculate_HipExtAngle(self,data) #

        # Give haptic feedback (turn feedback nodes on/off)
        if self.config['isFeedbackOn'] == "Yes": # and self.alreadyGivenFeedback == 0:
            self.Hip_ext = Hip_ext

            '''
            ** ORIGINALLY NOT COMMENTED OUT **
            '''
            # HipExt_funcs.give_feedback(self) #


            '''
            ** ADDED TO CODE **
            '''
            if self.Hip_ext > self.feedback_min:
                HipExt_funcs.give_feedback(self)


        time_now = self.iteration / self.DATARATE # time in seconds

        # my_data = {'time': [time_now],
                   # 'Gait_Phase': [self.gaitphase]}

        '''
        ** ADDED Gait_Phase **
        '''
        my_data = {'time': [time_now],
                   'Hip_ext': [Hip_ext],
                   'Feedback_min': [self.feedback_min],
                   'Feedback_max': [self.feedback_max],
                   'Gait_Phase': [self.gaitphase]}
        self.my_sage.save_data(data, my_data)
        self.my_sage.send_stream_data(data, my_data)
        return True

###########################################################
# Only for testing, don't modify
###########################################################
if __name__ == '__main__':
    # This is only for testing. make sure you do the pairing first in web api
    from sage.sage import Sage
    app = Core(Sage())
    app.test_run()
