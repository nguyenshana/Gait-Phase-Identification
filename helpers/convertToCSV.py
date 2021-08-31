import pandas as pd


'''
Converts the following sheets to csv:
1. Segment Orientation Quat
2. Joint Angles ZXY
3. Segment Acceleration
4. Segment Angular Velocity
'''
def makeCSVs(participantName, excelFilePath, csvFolder):

	sheets = {
				'Segment Orientation - Quat' : '-SegmentOrientationQuat.csv',
				'Joint Angles ZXY' : '-JointAnglesZXY.csv',
				'Segment Acceleration' : '-SegmentAcceleration.csv',
				'Segment Angular Velocity' : '-SegmentAngularVelocity.csv'
			 }

	print(participantName)

	for sheetName in sheets:

		read_file = pd.read_excel(excelFilePath, sheet_name=sheetName)
		read_file.to_csv(csvFolder + participantName + sheets[sheetName], index=None, header=True)

		print( 'Converted: {}'.format(sheetName) )




if __name__ == "__main__":

	# CHANGE THIS PATH TO WHERE THE EXCEL FILE(S) ARE
    pathToExcelFolder = '/Users/shana/Desktop/DesktopItems/BIOFEEDBACK/data/'

    # CHANGE THIS PATH TO WHERE YOU WANT THE CSV TO BE EXPORTED
    pathToCSVFolder = pathToExcelFolder + 'csv/'
    

    print('** START CONVERTING FILES ... **')

    # CHANGE THIS TO BE THE FILES THAT YOU WANT

    makeCSVs('p701', pathToExcelFolder + 'F007-001.xlsx', pathToCSVFolder)
    makeCSVs('p801', pathToExcelFolder + 'F008-001.xlsx', pathToCSVFolder)
    makeCSVs('p905', pathToExcelFolder + 'F009-005.xlsx', pathToCSVFolder)

    # makeCSVs('pF901', pathToExcelFolder + 'F009-001.xlsx', pathToCSVFolder)
    # makeCSVs('pF1001', pathToExcelFolder + 'F010-001.xlsx', pathToCSVFolder)
    # makeCSVs('pF1109', pathToExcelFolder + 'F011-009.xlsx', pathToCSVFolder)
    # makeCSVs('pF1209', pathToExcelFolder + 'F012-009.xlsx', pathToCSVFolder)
    # makeCSVs('pM801', pathToExcelFolder + 'M008-001.xlsx', pathToCSVFolder)
    # makeCSVs('pM908', pathToExcelFolder + 'M009-008.xlsx', pathToCSVFolder)
    # makeCSVs('pM1001', pathToExcelFolder + 'M010-001.xlsx', pathToCSVFolder)
    # makeCSVs('pM1101', pathToExcelFolder + 'M011-001.xlsx', pathToCSVFolder)
    # makeCSVs('pM1209', pathToExcelFolder + 'M012-009.xlsx', pathToCSVFolder)


    print('** SUCCESS :) **')
