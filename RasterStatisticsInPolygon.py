import arcpy


def main():
    try:
        # Check License
        if arcpy.CheckExtension("Spatial") == 'Available':
            arcpy.CheckOutExtension("Spatial")
            arcpy.AddMessage("SA License activated")
    except:
        arcpy.AddError("SA licence could not be loaded")
        return
    if arcpy.GetArgumentCount() != 5:
        arcpy.AddError("Invalid parameters")
        return None
    inRaster = arcpy.GetParameterAsText(0)
    inFeature= arcpy.GetParameterAsText(1)
    inFeatureID = arcpy.GetParameterAsText(2)
    statistics =  arcpy.GetParameterAsText(3)
    outFeature = arcpy.GetParameterAsText(4)
    outShape = outFeature+"_shp"

    workspace = arcpy.env.workspace
    arcpy.env.overwriteOutput = True

    arcpy.CopyFeatures_management(inFeature,outShape)
    arcpy.DefineProjection_management(outShape,arcpy.Describe(inFeature).spatialReference)
    arcpy.AddMessage("Starting Zonal Statistics")
    statTable = r'in_memory\statisticsTable'
    arcpy.sa.ZonalStatisticsAsTable(outShape,inFeatureID,inRaster,statTable,"DATA",statistics)
    arcpy.TableToTable_conversion(statTable,workspace,outFeature+"_Table")
    arcpy.AddMessage("Joining and creating layer")
    layer = outFeature+"_Layer"
    arcpy.MakeFeatureLayer_management(outShape,layer)
    arcpy.AddJoin_management(layer,inFeatureID,outFeature+"_Table",inFeatureID)
    arcpy.FeatureClassToFeatureClass_conversion(layer,workspace,outFeature)
    #Cleanup
    arcpy.Delete_management(outShape)
    arcpy.Delete_management("in_memory\statisticsTable")

    try:
        arcpy.CheckInExtension("Spatial")
    except:
        arcpy.AddError("Could not free SA license")

main()