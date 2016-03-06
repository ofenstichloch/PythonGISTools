import arcpy
import math

class ArtificialGrid:
    grid = []
    centers = []
    origin = arcpy.Point()
    end = arcpy.Point()
    radius = -1
    xOffset = 0
    yOffset = 0

    def createGrid(self,origin,end,cellType,align,cellSize,outShape):
        width = end.X-origin.X
        height = end.Y - origin.Y
        xOffset = 0
        yOffset = 0
        if cellType == "Hexagon": #switchcase is bad smell
            #Calculate the offset to shift the grid
            #X: Center bottom row
            #Y: Calculate how many double-rows are needed and check if you can leave out one
            if align =="true":

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
            self.constructHexagonsBySize(origin, end, cellSize/2,xOffset,yOffset,outShape)
        elif cellType == "Square":
            if align == "true":
                xOffset = -(math.ceil(width/cellSize)*cellSize-width)/2
                yOffset = -(math.ceil(height/cellSize)*cellSize-height)/2
            self.constructSquaresBySize(origin, end, cellSize,xOffset,yOffset, outShape)



    def constructHexagonsBySize(self, origin, end, radius, xOffset, yOffset, feature):
        self.radius = radius
        self.origin = origin
        self.end = end
        self.xOffset = xOffset
        self.yOffset = yOffset
        try:
            self.createHexagonCenterPoints()
        except Exception as e:
            arcpy.AddError("An error has occurred generating the center points for the shapes")
            arcpy.AddError(e.message)
        try:
            self.createHexagons()
        except Exception as e:
            arcpy.AddError("An error has occurred generating polygons")
            arcpy.AddError(e.message)
        arcpy.CopyFeatures_management(self.grid,feature)
        try:
            self.addIDs(feature)
        except Exception as e:
            arcpy.AddError("An error has occurred numbering the generated polygons")
            arcpy.AddError(e.message)

    def addIDs(self,feature):
        arcpy.AddField_management(feature,"ID","LONG","","","","","NULLABLE","REQUIRED")
        cursor = arcpy.UpdateCursor(feature)
        i=0
        for row in cursor:
            row.ID = i
            i=i+1
            cursor.updateRow(row)

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

    def constructSquaresBySize(self, origin, end, length, xOffset, yOffset, feature):
        self.radius = length
        self.origin = origin
        self.end = end
        self.xOffset = xOffset
        self.yOffset = yOffset
        try:
            self.createSquares()
            arcpy.CopyFeatures_management(self.grid,feature)
        except Exception as e:
            arcpy.AddError("An error has occurred generating the squares")
            arcpy.AddError(e.message)
        try:
            self.addIDs(feature)
        except Exception as e:
            arcpy.AddError("An error has occurred numbering the generated polygons")
            arcpy.AddError(e.message)

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
