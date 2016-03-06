import arcpy

#TODO:
#Check: Extent,


def main():
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
    arcpy.DefineProjection_management(outShape,arcpy.Describe(inRaster).spatialReference)
    arcpy.AddMessage("Starting Zonal Statistics")
    statTable = r'in_memory\statisticsTable'
    arcpy.sa.ZonalStatisticsAsTable(outShape,"ID",inRaster,statTable,"DATA",statistics)
    arcpy.TableToTable_conversion(statTable,workspace,outFeature+"_Table")
    arcpy.AddMessage("Joining and creating layer")
    layer = outFeature+"_Layer"
    arcpy.MakeFeatureLayer_management(outShape,layer)
    arcpy.AddJoin_management(layer,"ID",outFeature+"_Table","ID")
    arcpy.FeatureClassToFeatureClass_conversion(layer,workspace,outFeature)
    #Cleanup
    arcpy.Delete_management(outShape)

main()