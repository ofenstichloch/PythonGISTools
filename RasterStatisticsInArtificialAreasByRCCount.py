import arcpy
import math
from ArtificialGrid import ArtificialGrid

#TODO:
#Check addin
#check version to use arcpy.da


def main():
    #Check Input--------------------------------------------------------------------------------------------------------
    if arcpy.GetArgumentCount() != 7:
        arcpy.AddError("Invalid parameters")
        return None
    inRaster = arcpy.GetParameterAsText(0) #Input Raster dataset
    count = int(arcpy.GetParameterAsText(1))
    countType = arcpy.GetParameterAsText(2)
    cellType = arcpy.GetParameterAsText(3)
    align = arcpy.GetParameterAsText(4)
    statisticsType =  arcpy.GetParameterAsText(5) #Statistic type as supported by ZonalStatisticsAsTable
    outFeature = arcpy.GetParameterAsText(6) #Output Feature path
    arcpy.env.overwriteOutput = True
    workspace = arcpy.env.workspace
    outShape = outFeature+"_shp"
    if count <=0:
        arcpy.AddError("Invalid row/col count")
        return
    if outFeature == "": return

    #Generate grid------------------------------------------------------------------------------------------------------
    origin = arcpy.sa.Raster(inRaster).extent.lowerLeft #Origin in ArcMap is lower left corner
    end = arcpy.sa.Raster(inRaster).extent.upperRight
    width = end.X-origin.X
    height = end.Y - origin.Y
    if countType == "Rows":
        cellSize = height/count
    else:
        cellSize = width/count
    arcpy.AddMessage(cellSize)
    arcpy.AddMessage(width)
    grid = ArtificialGrid()
    ArtificialGrid.createGrid(grid,origin,end,cellType,align,cellSize,outShape)



    #Create Layer and join table----------------------------------------------------------------------------------------
    try:
        arcpy.DefineProjection_management(outShape,arcpy.Describe(inRaster).spatialReference)
    except Exception as e:
        arcpy.AddMessage("Could not alter spatial reference")
        arcpy.AddMessage(e.message)
    arcpy.AddMessage("Starting Zonal Statistics")
    statTable = r'in_memory\statisticsTable'
    try:
        arcpy.sa.ZonalStatisticsAsTable(outShape,"ID",inRaster,statTable,"DATA",statisticsType)
        arcpy.TableToTable_conversion(statTable,workspace,outFeature+"_Table")
    except Exception as e:
        arcpy.AddMessage("Could not crete zonal statistics")
        arcpy.AddMessage(e.message)
    arcpy.AddMessage("Joining and creating layer")
    layer = outFeature+"_Layer"
    try:
        arcpy.MakeFeatureLayer_management(outShape,layer)
        arcpy.AddJoin_management(layer,"ID",outFeature+"_Table","ID")
        arcpy.FeatureClassToFeatureClass_conversion(layer,workspace,outFeature)
    except Exception as e:
        arcpy.AddMessage("Could not save final result")
        arcpy.AddMessage(e.message)
    #Cleanup
    try:
        arcpy.Delete_management(outShape)
    except Exception as e:
        arcpy.AddMessage("Could not delete temporary file")
        arcpy.AddMessage(e.message)



main()