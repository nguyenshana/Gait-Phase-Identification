# Gait-Phase-Identification

Algorithm to detect gait phase.

## Main code is in: main.py

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
