import arcpy
import math
#For ArcMap >= 10.2 use arcpy.da for better performance
try:
    from arcpy import da
    arcpy.AddMessage("Using Arcpy Data-Access")
    useDA=True
except:
    useDA=False

class ArtificialGrid:
    grid = []
    centers = []
    origin = arcpy.Point()
    end = arcpy.Point()
    radius = -1
    xOffset = 0
    yOffset = 0
    outShape = ""
    workspace = ""
    cursor = 0

    def createGrid(self,origin,end,cellType,align,cellSize,workspace, outShape, rows=-1, cols=-1):
        width = end.X-origin.X
        height = end.Y - origin.Y
        xOffset = 0
        yOffset = 0
        self.workspace = workspace
        self.outShape = outShape
        #If ArcMap version >=10.2 -> use arcpy.da for better performance
        if useDA:
            arcpy.CreateFeatureclass_management(workspace,outShape,"POLYGON")
            arcpy.AddField_management(workspace+"\\"+outShape,"ID","LONG","","","","","NULLABLE","REQUIRED")
            self.cursor = arcpy.da.InsertCursor(workspace+"\\"+outShape,["ID","SHAPE@"])
            arcpy.AddMessage("Created shapefile "+workspace+"\\"+outShape)

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
            self.constructHexagonsBySize(origin, end, cellSize/2,xOffset,yOffset, rows, cols)
        elif cellType == "Square":
            if align == "true":
                xOffset = -(math.ceil(width/cellSize)*cellSize-width)/2
                yOffset = -(math.ceil(height/cellSize)*cellSize-height)/2
            self.constructSquaresBySize(origin, end, cellSize,xOffset,yOffset, rows, cols)
        arcpy.AddMessage("Created grid")
        del self.cursor



    def constructHexagonsBySize(self, origin, end, radius, xOffset, yOffset, rows, cols):
        self.radius = radius
        self.origin = origin
        self.end = end
        self.xOffset = xOffset
        self.yOffset = yOffset
        try:
            self.createHexagonCenterPoints(rows, cols)
        except Exception as e:
            arcpy.AddError("An error has occurred generating the center points for the shapes")
            arcpy.AddError(e.message)
        try:
            self.createHexagons()
        except Exception as e:
            arcpy.AddError("An error has occurred generating polygons")
            arcpy.AddError(e.message)
        #arcpy.da insertcursor already did that:
        if not useDA:
            arcpy.CopyFeatures_management(self.grid,self.workspace+"\\"+self.outShape)
            try:
                self.addIDs()
            except Exception as e:
                arcpy.AddError("An error has occurred numbering the generated polygons")
                arcpy.AddError(e.message)

    def addIDs(self):
        arcpy.AddField_management(self.workspace+"\\"+self.outShape,"ID","LONG","","","","","NULLABLE","REQUIRED")
        cursor = arcpy.UpdateCursor(self.workspace+"\\"+self.outShape)
        i=0
        for row in cursor:
            row.ID = i
            i=i+1
            cursor.updateRow(row)

    def createHexagonCenterPoints(self,rows,cols):
        countRows = True if rows!=-1 else False
        countCols = True if cols!=-1 else False
        colsOld = cols
        currentY = self.origin.Y+self.radius/2+self.yOffset
        even = False
        while ((currentY-self.radius/2 < self.end.Y and even) or (currentY-self.radius < self.end.Y and not even)) and (rows > 0 or not countRows): #Generate rows until extent reached
            if even:
                currentX=self.origin.X+self.xOffset
                cols = colsOld + 1
                even = False
            else:
                currentX = self.origin.X+self.radius+self.xOffset
                cols = colsOld
                even = True
            while currentX-self.radius < self.end.X and (cols > 0 or not countCols): #Fill rows until extent reached
                self.centers.append(arcpy.Point(currentX,currentY))
                currentX+=2*self.radius
                cols=cols-1
            currentY+=1.5*self.radius
            rows = rows - 1

    def createHexagons(self):
        hexagons = []
        i=0
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
            if useDA:
                self.cursor.insertRow([i,arcpy.Polygon(hexagon)])
                i=i+1
        self.grid = list(hexagons)

    def constructSquaresBySize(self, origin, end, length, xOffset, yOffset, rows, cols):
        self.radius = length
        self.origin = origin
        self.end = end
        self.xOffset = xOffset
        self.yOffset = yOffset
        try:
            self.createSquares(rows, cols)
            arcpy.CopyFeatures_management(self.grid,self.workspace+"\\"+self.outShape)
        except Exception as e:
            arcpy.AddError("An error has occurred generating the squares")
            arcpy.AddError(e.message)
        try:
            self.addIDs()
        except Exception as e:
            arcpy.AddError("An error has occurred numbering the generated polygons")
            arcpy.AddError(e.message)

    def createSquares(self,rows, cols):
        countRows = True if rows!=-1 else False
        countCols = True if cols!=-1 else False
        currentY = self.origin.Y+self.yOffset
        colsOld = cols
        while currentY < self.end.Y and (not countRows or rows > 0):
            i=0
            currentX = self.origin.X+self.xOffset
            cols = colsOld
            while currentX < self.end.X and (not countCols or cols >0):
                square = arcpy.Array()
                square.append(arcpy.Point(currentX,currentY))
                square.append(arcpy.Point(currentX+self.radius,currentY))
                square.append(arcpy.Point(currentX+self.radius,currentY+self.radius))
                square.append(arcpy.Point(currentX,currentY+self.radius))
                square.append(square[0])
                self.grid.append(arcpy.Polygon(square))
                currentX+=self.radius
                cols =cols -1
                if useDA:
                    self.cursor.insertRow([i,arcpy.Polygon(square)])
                    i=i+1
            currentY+=self.radius
            rows = rows -1
