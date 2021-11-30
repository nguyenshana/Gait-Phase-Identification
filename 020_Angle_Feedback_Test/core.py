import logging
from sage.base_app import BaseApp
if __name__ == '__main__':
    import TSA_functions
    import HipExt_funcs
else:
    from . import TSA_functions
    from . import HipExt_funcs



class Core(BaseApp):
###########################################################
# INITIALIZE APP

# 'original' = TSA_functions folder 02010
###########################################################
    def __init__(self, my_sage):
        BaseApp.__init__(self, my_sage, __file__)

        '''
        *** FROM HIPEXT FOLDER 01111 *** 

        '''

        # self.gaitphase = 'swing' # default gait phase
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

        # self.iteration = 0
        self.iters_consecutive_below_thresh_gyroMag_heelstrike = 0
        self.iters_consecutive_above_thresh_gyroMag_toeoff = 0
        self.iters_since_last_heelstrike = 0

        self.feedback_min = 0
        self.feedback_max = 0

        self.alreadyGivenFeedback = 0
        self.thigh_Yawoffset_q = [1,0,0,0]

        self.BS_q_pelvis_inv = [1,0,0,0]  # sensor to segment alignment quaternion, inv denotes conjugate.
        self.BS_q_thigh_inv = [1,0,0,0]


        '''
        *** ORIGINAL *** 

        '''

        # Set up the app
        # coding guide: The prefix "self" denotes global variable
        self.iteration = 0
        self.stepnum = 0
        self.my_sage.register_sensor_button_callback(self.call_back_fcn1)
        self.my_sage.register_feedback_button_callback(self.call_back_fcn2)
        self.my_sage.register_function_button_callback(self.call_back_fcn3)
        self.TSA_array = []
        self.TSA_min_this_step = 0
        self.TSA_max_this_step = 0

        self.gaitphase = 'swing' # default gait phase
        # self.stridetime = self.config['stride_time']
        # self.stancetime = 0.6*self.stridetime

        self.stridetime_changing = 1

        self.iterations_below_gyroMag_thresh = 0
        self.iterations_since_last_heelstrike = 100000 # make this very large as default

        self.fnc_button = 0

###########################################################
# CHECK NODE CONNECTIONS
###########################################################
    def check_status(self):
        # check if the requirement if satisfied
        sensors_count = self.get_sensors_count()
        feedback_count = self.get_feedback_count()
        logging.debug("config pulse length {}".format(self.info["pulse_length"]))
        err_msg = ""
        if sensors_count < len(self.info['sensors']):
            err_msg += "App requires {} sensors but only {} are connected".format(
                    len(self.info['sensors']), sensors_count)
        if self.config['feedback_enabled'] and feedback_count < len(self.info['feedback']):
            err_msg += "App require {} feedback but only {} are connected".format(
                    len(self.info['feedback']), feedback_count)
        if err_msg != "":
            return False, err_msg
        return True, "Now running Trunk Sway app"

#############################################################
# WRITE ALGORITHM IN BLOCK BELOW
#############################################################
#       coding guide: main loop of user app.
    def run_in_loop(self):
        # Get next data packet
        data = self.my_sage.get_next_data()

        # Definitions
        UPDATE_RATE = 50 #Hz
        node_num_TSA = 0
        node_num_heelstrike = 1

        # Test axes directions for specific node
#        node_num = 0
#        TSA_functions.test_node_axes_directions(node_num,data)

        gaitphase_last = self.gaitphase
        if self.stepnum < 1:
            iterations_since_last_heelstrike_previous = 50
        else:
            iterations_since_last_heelstrike_previous = self.iterations_since_last_heelstrike


        # Determine gait phase
        # in1 = self.gaitphase
        # in2 = self.stancetime
        # in3 = self.iterations_below_gyroMag_thresh
        # in4 = self.iterations_since_last_heelstrike
        # in5 = node_num_heelstrike
        # in6 = data
        # in7 = UPDATE_RATE

        #(out1,out2,out3) = TSA_functions.get_gaitphase(in1,in2,in3,in4,in5,in6,in7)
        out1 = 1
        out2 = 1
        out3 = 1

        self.gaitphase = 0
        self.iterations_below_gyroMag_thresh = 0
        self.iterations_since_last_heelstrike = 0

        gaitphase_this = self.gaitphase

        # coding guide: core algorithm
        # Calculate the Trunk Sway Angle (TSA)
        TSA = TSA_functions.calculate_TSA(node_num_TSA,data)
        # TSA = TSA - self.config['ts_offset']
        self.TSA_array.append(TSA)

        logging.debug("TSA: {:.1f}, below gyro: {}, since heelstrike: {}   {}".format(
            TSA,out2,out3,out1))
        logging.debug("TSA: {:.1f}, below gyro: {}, since heelstrike: {}   {}".format(
            TSA,out2,out3,out1))


        # Get min and max TSA values for last step
        TSA_array = []
        self.TSA_min_this_step = self.config['angle_min']
        self.TSA_max_this_step = self.config['angle_max']
        TSA_min_this_step = self.config['angle_min']
        TSA_max_this_step = self.config['angle_max']
        self.TSA_array = TSA_array


        # Get current step number
        #this_stepnum = TSA_functions.get_stepnum(gaitphase_last,gaitphase_this,self.stepnum)
        this_stepnum=0
        self.stepnum = this_stepnum


        # Get current stride time
        this_stridetime_changing = TSA_functions.get_stridetime(gaitphase_last,gaitphase_this,UPDATE_RATE,iterations_since_last_heelstrike_previous,self.stridetime_changing)
        self.stridetime_changing = this_stridetime_changing
        logging.debug("TSA: {:.1f}, below gyro: {}, since heelstrike: {}   {}".format(
            TSA,out2,out3,out1))


        # Turn feedback nodes on/off
        #if self.gaitphase == 'stance_mid':
        # coding guide: the value of self.config comes from the value we set in app configuration area, the value of self.info comes from info.json
        TSA_min = self.config['angle_min'] # min trunk sway angle w/ no feedback
        TSA_max = self.config['angle_max'] # max trunk sway angle w/ no feedback

        if self.config['feedback_enabled']:
            if TSA < TSA_min:
                if self.info['push_or_pull'] == 'push':
                    self.my_sage.feedback_on(1,self.info["pulse_length"])
                    feedback0 = 0
                    feedback1 = 1
                elif self.info['push_or_pull'] == 'pull':
                    self.my_sage.feedback_on(0, self.info["pulse_length"])
                    feedback0 = 1
                    feedback1 = 0
            elif TSA > TSA_max:
                if self.info['push_or_pull'] == 'push':
                    self.my_sage.feedback_on(0,self.info["pulse_length"])
                    feedback0 = 1
                    feedback1 = 0
                elif self.info['push_or_pull'] == 'pull':
                    self.my_sage.feedback_on(1, self.info["pulse_length"])
                    feedback0 = 0
                    feedback1 = 1
            else:
                self.my_sage.feedback_off(0)
                self.my_sage.feedback_off(1)
                feedback0 = 0
                feedback1 = 0
        else:
            feedback0 = 0
            feedback1 = 0

        # Increment and save data
        self.iteration += 1
#        if self.iteration % 100 == 0:
#            print("Iteration {}".format(self.iteration))  # coding guide: print debug information.
#        my_data = {'iteration': [self.iteration]}
#       coding guide: if you want to show more data in GUI, add it here.
        my_data = {
        
                   # from HipExt folder 01111
                   'Hip_ext': [Hip_ext],
                   'Feedback_min': [self.feedback_min],
                   'Feedback_max': [self.feedback_max],

                   # 'original'
                   'time': [self.iteration/self.info["datarate"]],
                   'angle': [TSA],
                   'angle_min': [TSA_min_this_step],
                   'angle_max': [TSA_max_this_step],
                   'feedback1': [feedback0],
                   'feedback2': [feedback1],
                   'fnc_button': [self.fnc_button]}


        self.my_sage.save_data(data, my_data)
        self.my_sage.send_stream_data(data, my_data)
        return True
#############################################################

    def call_back_fcn1(self, index, event):
        if event == self.my_sage.BUTTON_DOWN:
            self.fnc_button += 1

    def call_back_fcn2(self, index, event):
        if event == self.my_sage.BUTTON_DOWN:
            self.fnc_button += 1

    def call_back_fcn3(self, event):
        if event == self.my_sage.BUTTON_DOWN:
            self.fnc_button += 1


if __name__ == '__main__':
    # This is only for testing. make sure you do the pairing first in web api
    from sage.sage import Sage
    app = Core(Sage())
    app.test_run()
