import arcpy
import math
from ArtificialGrid import ArtificialGrid

#1. Read Input
#2. Generate specific Areas
#3. Calculate

def main():
    try:
        # Check License
        if arcpy.CheckExtension("Spatial") == 'Available':
            arcpy.CheckOutExtension("Spatial")
            arcpy.AddMessage("SA License activated")
    except:
        arcpy.AddError("SA licence could not be loaded")
        return
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

    try:
        ArtificialGrid.createGrid(grid,origin,end,cellType,align,cellSize,workspace,outShape)
        #Create Layer and join table
        arcpy.DefineProjection_management(outShape,arcpy.Describe(inRaster).spatialReference)
        arcpy.AddMessage("Starting Zonal Statistics")
        statTable = r'in_memory\statisticsTable'
        arcpy.sa.ZonalStatisticsAsTable(workspace+"\\"+outShape,"ID",inRaster,statTable,"DATA",statisticsType)
        arcpy.TableToTable_conversion(statTable,workspace,outFeature+"_Table")
        arcpy.AddMessage("Joining and creating layer")
        layer = outFeature+"_Layer"
        arcpy.MakeFeatureLayer_management(outShape,layer)
        arcpy.AddJoin_management(layer,"ID",outFeature+"_Table","ID")
        arcpy.FeatureClassToFeatureClass_conversion(layer,workspace,outFeature)
    except Exception as e:
        arcpy.AddError(e.message)
    finally:
        try:
            arcpy.Delete_management(outShape)
            arcpy.Delete_management("in_memory\statisticsTable")
        except Exception as e:
            arcpy.AddError("Could not delete temporary file")
            arcpy.AddError(e.message)
    try:
        arcpy.CheckInExtension("Spatial")
    except:
        arcpy.AddError("Could not free SA license")


main()