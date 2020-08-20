# Description: Creates a point feature class from input table

# import system modules 
import arcpy

# inputs
directory = 'C:\\Users\\benne\\PycharmProjects\\caes\\projects\\mid_atlantic\\bct_fixed'
filegeodatabase = 'results.gdb' # Needs to be created ahead of time
files = ['results_LK1.csv','results_MK1-3.csv', 'results_UJ1.csv']
variable = 'RTE'
rasterNames = ['LK1_RTE','MK1_3_RTE','UJ1_RTE']

# Set environment settings
arcpy.env.workspace = directory+'\\'+filegeodatabase

# Enable overwrite
arcpy.env.overwriteOutput = True

for file, rasterName in zip(files, rasterNames):

	# Set the local variables
	in_table = directory+'\\'+file
	out_feature_class = "points_"+file
	x_coords = "X (m)"
	y_coords = "Y (m)"
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
