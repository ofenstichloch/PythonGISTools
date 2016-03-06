import arcpy
import math
from ArtificialGrid import ArtificialGrid

#TODO:
#Check addin
#check version to use arcpy.da


#Fragen:
#Wie funktioniert ein JOIN, sodass arcmap den auch erkennt? Doc hilft nicht weiter
#Warum extent angeben? Damit lassen sich keine shapes erzeugen

#1. Read Input
#2. Generate specific Areas
#3. Calculate

def main():
    #Check Input--------------------------------------------------------------------------------------------------------
    if arcpy.GetArgumentCount() != 6:
        arcpy.AddError("Invalid parameters")
        return None
    inRaster = arcpy.GetParameterAsText(0) #Input Raster dataset
    cellSize = float(arcpy.GetParameterAsText(1).replace(",",".")) #Input cell Size of artificial grid in Pixel on Raster
    cellType = arcpy.GetParameterAsText(2)
    align = arcpy.GetParameterAsText(3)
    statisticsType =  arcpy.GetParameterAsText(4) #Statistic type as supported by ZonalStatisticsAsTable
    outFeature = arcpy.GetParameterAsText(5) #Output Feature path
    arcpy.env.overwriteOutput = True
    workspace = arcpy.env.workspace
    outShape = outFeature+"_shp"
    if cellSize <=0:
        arcpy.AddError("Invalid cellSize")
        return
    if outFeature == "": return

    #Generate grid------------------------------------------------------------------------------------------------------
    origin = arcpy.sa.Raster(inRaster).extent.lowerLeft #Origin in ArcMap is lower left corner
    end = arcpy.sa.Raster(inRaster).extent.upperRight
    grid = ArtificialGrid()
    ArtificialGrid.createGrid(grid,origin,end,cellType,align,cellSize,outShape)


    #Create Layer and join table
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
        arcpy.Delete_management("in_memory\statisticsTable")
    except Exception as e:
        arcpy.AddMessage("Could not delete temporary file")
        arcpy.AddMessage(e.message)



main()