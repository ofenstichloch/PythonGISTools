import arcpy

#TODO:
#Check: Extent,
#Make Parameter StatisticType as Dropdown


def main():
    if arcpy.GetArgumentCount() != 5:
        arcpy.AddError("Invalid parameters")
        return None
    inRaster = arcpy.GetParameterAsText(0)
    inFeature= arcpy.GetParameterAsText(1)
    inFeatureID = arcpy.GetParameterAsText(2)
    statistics =  arcpy.GetParameterAsText(3)
    outFeature = arcpy.GetParameterAsText(4)

    workspace = arcpy.env.workspace
    arcpy.env.overwriteOutput = True
    arcpy.AddMessage("Reading Input")
    arcpy.CopyFeatures_management(inFeature,outFeature)
    arcpy.AddMessage("Starting Zonal Statistics")
    statTable = r'in_memory\statisticsTable'
    arcpy.sa.ZonalStatisticsAsTable(outFeature,inFeatureID,inRaster,statTable,"DATA",statistics)
    arcpy.AddMessage("Joining...")
    arcpy.JoinField_management(outFeature,inFeatureID,statTable,inFeatureID)
    arcpy.AddMessage("Done")

main()