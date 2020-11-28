# Gait-Phase-Identification

Algorithm to detect gait phase. Currently is based off of excel data with a frame rate of 60 Hz.
Can be altered to detect in real time.

## Setup to do before running the program


### Change Excel Data
Remember to change (or at least check):
1. Set staring row amount
2. Set filepath variable
3. Set column name (if necessary)
4. excel_data_df needs to read the new file
5. Set input length
6. Add chart title [the part that says: ax.set_title(...)]

If using other excel sheets that are formatted differently than Participant 14 Trial 1 & 2, you'll need to change the sheet name variable and the column number (I believe column numbering starts at 0) in excel_data_df.


## What I use to run the code
I like using Spyder as my IDE because it has a console and a place where graphs show up, but you can run it however you like!
