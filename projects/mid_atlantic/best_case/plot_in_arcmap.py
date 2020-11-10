# Description: Creates a point feature class from input table

# import system modules 
import arcpy

# inputs
directory = 'C:\\Users\\benne\\PycharmProjects\\caes\\projects\\mid_atlantic\\best_case'
filegeodatabase = 'results.gdb' # Needs to be created ahead of time
files = ['LK1_analysis.csv','MK1-3_analysis.csv', 'UJ1_analysis.csv']
variable = 'RTE_mean'
rasterNames = ['LK1_results','MK1_3_results','UJ1_results']

# Set environment settings
arcpy.env.workspace = directory+'\\'+filegeodatabase

# Enable overwrite
arcpy.env.overwriteOutput = True

for file, rasterName in zip(files, rasterNames):

	# Set the local variables
	in_table = directory+'\\'+file
	out_feature_class = "points_"+file
	x_coords = "X_m"
	y_coords = "Y_m"
	spRef = arcpy.SpatialReference("NAD 1983 UTM Zone 19N")

	# Make the XY event layer...
	arcpy.MakeXYEventLayer_management(in_table, x_coords, y_coords, out_feature_class, spRef)

	# Execute PointToRaster
	valField = variable
	outRaster = rasterName
	cellSize = 19790 # meters
	assignmentType = "MEAN"
	priorityField = ""
	result = arcpy.PointToRaster_conversion(out_feature_class, valField, outRaster, assignmentType, priorityField, cellSize)
