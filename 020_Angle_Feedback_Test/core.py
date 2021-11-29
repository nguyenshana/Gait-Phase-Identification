import logging
from sage.base_app import BaseApp
if __name__ == '__main__':
    import subfunctions
else:
    from . import subfunctions

class Core(BaseApp):
###########################################################
# INITIALIZE APP
###########################################################
    def __init__(self, my_sage):
        BaseApp.__init__(self, my_sage, __file__)

        # Set up the app
        # The prefix "self" denotes global variables 
        self.iteration = 0


###########################################################
# CHECK NODE CONNECTIONS
###########################################################
    def check_status(self):
        # check if the requirement is satisfied
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
        return True, "Now running Angle Feedback Test App"

#############################################################
# RUN APP IN LOOP
#############################################################
    # Main loop of the user app     
    def run_in_loop(self):
        # Get next data packet
        data = self.my_sage.get_next_data()

        # Define the node number for sesning this_angle
        node_num_this_angle = 0

        # Calibrate and calculate angle
        if self.iteration == 0:
            BS_q_pelvis_inv, BS_q_thigh_inv = subfunctions.calibrate(data) 

        (Hip_flex, Hip_abd, Hip_rot) = subfunctions.calculate_HipExtAngle(data, BS_q_pelvis_inv, BS_q_thigh_inv)

        hipAngle = Hip_flex

        # * * *
        # DEFAULT code to calculate angle:
        # * * *
        # this_angle = subfunctions.calculate_angle(node_num_this_angle,data)


        # Turn feedback nodes on/off
        # self.config values are set in the App Configuration panel of the SageMotion Graphical Interface
        this_angle_min = self.config['angle_min'] #  minimum angle with no feedback
        this_angle_max = self.config['angle_max'] #  maximum angle with no feedback

        if self.config['feedback_enabled']:
            # if this_angle < this_angle_min:
            if hipAngle < this_angle_min:
                # self.info values come from the file info.json 
                self.my_sage.feedback_on(0, self.info["pulse_length"])
                feedback0 = 1
                feedback1 = 0
            elif hipAngle > this_angle_max:
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
        
        # Print out real-time debegging info in the Graphical Interface > Developers (bottom left link) > App Log
        if self.iteration % 100 == 0:
            print("Iteration {}".format(self.iteration))  
            # print("This angle is: {:.2f}".format(this_angle))
            print("This angle is: {:.2f}".format(hipAngle))
            print("")
            
        # To save data, add it to the my_data structure and update the user_fields in info.json accordingly 
        my_data = {'time': [self.iteration/self.info["datarate"]],
                   'angle': [this_angle],
                   'angle_min': [this_angle_min],
                   'angle_max': [this_angle_max],
                   'feedback1': [feedback0],
                   'feedback2': [feedback1]}

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
