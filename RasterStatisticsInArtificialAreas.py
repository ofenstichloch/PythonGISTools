import arcpy
import math

#TODO:
#Set target Feature spacial reference
#Check addin
#Add bool value to center the new extent features -> calculate row/column count (ceil(extent/radius)) then define offset to center new objects



#1. Read Input
#2. Generate specific Areas
#3. Calculate

'''
INFO: Centering the grid may lead to a non minimal solution


'''
def main():
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

    #Generating grid
    origin = arcpy.sa.Raster(inRaster).extent.lowerLeft #Origin in ArcMap is lower left corner
    end = arcpy.sa.Raster(inRaster).extent.upperRight
    grid = ArtificialGrid()
    xOffset = 0
    yOffset = 0
    if cellType == "Hexagon": #switchcase is bad smell
        #Calculate the offset to shift the grid
        #X: trivial
        #Y: Calculate how many double-rows are needed and check if you can leave out one
        if align =="true":
            width = float( arcpy.sa.Raster(inRaster).extent.width)
            height = float( arcpy.sa.Raster(inRaster).extent.height)
            xOffset = -(math.ceil(width/cellSize)*cellSize-width)/2
            #yOverhead: Expect an even number of rows, thus 1.5*cellSize each double-row
            yOverhead = math.ceil(height/(1.5*cellSize))*cellSize*1.5-height
            #If you can leave out a complete row:
            if yOverhead > cellSize:
                yOverhead-=cellSize
            #If you need another row to fill the small gaps between the triangles
            elif yOverhead < cellSize/4:
                yOverhead+=cellSize/2
            #Subtract the upper triangles because the ones on the bottom edge are not counted in either
            else:
                yOverhead -= cellSize/4
            yOffset = -yOverhead/2
        grid = ArtificialGrid.constructHexagonsBySize(grid, origin, end, cellSize/2,xOffset,yOffset)
    elif cellType == "Square":
        if align == "true":
            width = float( arcpy.sa.Raster(inRaster).extent.width)
            height = float( arcpy.sa.Raster(inRaster).extent.height)
            xOffset = -(math.ceil(width/cellSize)*cellSize-width)/2
            yOffset = -(math.ceil(height/cellSize)*cellSize-height)/2
            arcpy.AddMessage(math.ceil(height/cellSize))
        grid = ArtificialGrid.constructSquaresBySize(grid, origin, end, cellSize,xOffset,yOffset)

    arcpy.CopyFeatures_management(grid,outFeature)



class ArtificialGrid:
    grid = []
    centers = []
    origin = arcpy.Point()
    end = arcpy.Point()
    radius = -1
    xOffset = 0
    yOffset = 0

    def constructHexagonsBySize(self, origin, end, radius, xOffset, yOffset):
        self.radius = radius
        self.origin = origin
        self.end = end
        self.xOffset = xOffset
        self.yOffset = yOffset
        self.createHexagonCenterPoints()
        self.createHexagons()
        return self.grid

    def createHexagonCenterPoints(self):
        currentY = self.origin.Y+self.radius/2+self.yOffset
        odd = False
        while (currentY-self.radius/2 < self.end.Y and odd) or (currentY-self.radius < self.end.Y and not odd) : #Generate rows until extent reached
            if odd:
                currentX=self.origin.X+self.xOffset
                odd = False
            else:
                currentX = self.origin.X+self.radius+self.xOffset
                odd = True
            while currentX-self.radius < self.end.X: #Fill rows until extent reached
                self.centers.append(arcpy.Point(currentX,currentY))
                currentX+=2*self.radius
            currentY+=1.5*self.radius

    def createHexagons(self):
        hexagons = []
        for p in self.centers:
            hexagon = arcpy.Array()
            hexagon.append(arcpy.Point(p.X+self.radius,p.Y+self.radius/2))
            hexagon.append(arcpy.Point(p.X,p.Y+self.radius))
            hexagon.append(arcpy.Point(p.X-self.radius,p.Y+self.radius/2))
            hexagon.append(arcpy.Point(p.X-self.radius,p.Y-self.radius/2))
            hexagon.append(arcpy.Point(p.X,p.Y-self.radius))
            hexagon.append(arcpy.Point(p.X+self.radius,p.Y-self.radius/2))
            hexagon.append(hexagon[0])
            hexagons.append( arcpy.Polygon(hexagon))
        self.grid = list(hexagons)

    def constructSquaresBySize(self, origin, end, length, xOffset, yOffset):
        self.radius = length
        self.origin = origin
        self.end = end
        self.xOffset = xOffset
        self.yOffset = yOffset
        self.createSquares()
        return self.grid

    def createSquares(self):
        currentY = self.origin.Y+self.yOffset
        while currentY < self.end.Y:
            currentX = self.origin.X+self.xOffset
            while currentX < self.end.X:
                square = arcpy.Array()
                square.append(arcpy.Point(currentX,currentY))
                square.append(arcpy.Point(currentX+self.radius,currentY))
                square.append(arcpy.Point(currentX+self.radius,currentY+self.radius))
                square.append(arcpy.Point(currentX,currentY+self.radius))
                square.append(square[0])
                self.grid.append(arcpy.Polygon(square))
                currentX+=self.radius
            currentY+=self.radius


main()