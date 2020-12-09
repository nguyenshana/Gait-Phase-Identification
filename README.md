# Gait-Phase-Identification

Algorithm to detect gait phase. Currently is based off of excel data with a frame rate of 60 Hz.
Can be altered to detect in real time.

## Setup to do before running the program (gyroscopeAlgorithm.py)


### Change Excel Data
Remember to change (or at least check):
1. Change pathToFolder to your path to the excel files (line 31)
2. Check if frequency is correct (line 88)
3. Set participant name (line 94) (possible names are in 'trials' on line 38)
4. Run the code

excel_data_df in the setParticipant function has excel sheet names and indexes.


## What I use to run the code
I like using Spyder as my IDE because it has a console and a place where graphs show up, but you can run it however you like!
