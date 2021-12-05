# Gait-Phase-Identification

Algorithm to detect gait phase.

## SageMotion

The best folder to build upon is HipExt_SageMotion_01111

Folders:
- TSA_SageMotion_02010: 
	- from SageMotion UI
	- code not edited

- HipExt_SageMotion_01111:
	- from SageMotion UI
	- core.py slightly edited to use their provided gait segmentation algorithm
	- original code without gait segmentation was tested with the system and it worked
	- **best code to use**

- TSA_HipExt_SageMotion:
	- an attempt to combine TSA and HipExt code
	- copied TSA_SageMotion_02010 code and added some HipExt_SageMotion_01111 code


## Main code for XSENS testing is in: main.py

main.py uses some functions in sageMotionFunctions.py (which are functions provided by SageMotion), and gaitAlgorithms.py (which are gait detection algorithms)

## File Setup:

For main.py:

1. Change 'pathToFolder' variable in Main.getParticipantInfo() to have the correct path to csv file
2. Can change inputs at the very bottom

For shankAccelZMaxima.py (uses csv), hipCalc-SageMotion.py (excel), shankAccelZ.py (excel), footAVyshankAVz.py (excel), multipleSignals.py (excel):

1. Can change the inputs for main() at the very bottom
2. Change 'pathToFolder' variable in main() to have the correct path to your excel/csv files

For gyroscopeAlgorithm.py:

Remember to change (or at least check):
1. Change pathToFolder to your path to the excel files (line 31)
2. Check if frequency is correct (line 88)
3. Set participant name (line 94) (possible names are in 'trials' on line 38)
4. Run the code
