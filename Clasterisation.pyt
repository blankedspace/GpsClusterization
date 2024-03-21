import re
import arcpy
from EarthSphereLib import *
import EarthSphereLib
import Clastrization
imp.reload(EarthSphereLib)
import li_method
import imp
imp.reload(li_method)
import copy
import math

class Toolbox(object):
    def __init__(self):
        """Define the toolbox (the name of the toolbox is the name of the
        .pyt file)."""
        self.label = "GPS"
        self.alias = ""
      
        # List of tool classes associated with this toolbox
        self.tools = [Tool]

def calculate_bearing(x, y):
    # Calculate the angle in radians
    angle_rad = math.atan2(y, x)
    
    # Convert radians to degrees
    angle_deg = math.degrees(angle_rad)
    
    # Adjust the result to the range of 0 to 360 degrees
    if angle_deg < 0:
        angle_deg += 360
    elif angle_deg >= 360:
        angle_deg -= 360
    
    return angle_deg

class Tool(object):
    def __init__(self):
        """Define the tool (tool name is the name of the class)."""
        self.label = "Clasterization"
        self.description = ""
        self.canRunInBackground = False

    def getParameterInfo(self):
        """Define parameter definitions"""
        param0 = arcpy.Parameter(
            displayName="Input Features",
            name="in_features",
            datatype="GPLayer",
            parameterType="Required",
            direction="Input")
        
        param1 = arcpy.Parameter(
            displayName="Output path",
            name="out_features",
            datatype="DEFeatureClass",
            parameterType="Required",
            direction="Output")
        
        param2 = arcpy.Parameter(
            displayName="Output path Polus",
            name="out_features",
            datatype="DEFeatureClass",
            parameterType="Required",
            direction="Output")
        
        param3 = arcpy.Parameter(
            displayName="Error",
            name="err",
            datatype="GPLong",
            parameterType="Required",)
    
        param4 = arcpy.Parameter(
            displayName="MaxClasters",
            name="max_claster",
            datatype="GPLong",
            parameterType="Required",)
        
        
        params = [param0,param1,param2,param3,param4]
        return params

    def isLicensed(self):
        """Set whether tool is licensed to execute."""
        return True

    def updateParameters(self, parameters):
        """Modify the values and properties of parameters before internal
        validation is performed.  This method is called whenever a parameter
        has been changed."""
        return

    def updateMessages(self, parameters):
        """Modify the messages created by internal validation for each tool
        parameter.  This method is called after internal validation."""
        return

    def execute(self, parameters, messages):
        """The source code of the tool."""
        data = parameters[0].value
        arcpy.AddMessage(data)

        self.points = [] # type: [gps_point]
        with arcpy.da.SearchCursor(data, ["SHAPE@","Ve","Vn"]) as cursor:
            arcpy.AddMessage(cursor)
            for row in cursor:
                # Access the point geometry and attribute data for each row
                point_geometry = row[0]
                Ve = int(row[1])
                Ve = int(row[2])

                point = gps_point(float(point_geometry.centroid.X), float(point_geometry.centroid.Y))
                point.set_velocity(Vn=float(row[1]), Ve=float(row[2]))
                self.points.append(point)
                # Do something with the point geometry and attribute data
                arcpy.AddMessage("Point at ({}, {}) has ve value of {} and field2 value of ".format(point.lat, point_geometry.centroid.Y,row))
        

        self.claster = []
        Clastrization.ERR_RATE = parameters[3].value

        for i in range(parameters[4].value):
            cpy = copy.deepcopy(self.points)
            points = li_method.calculate(cpy)
            self.claster.append(points)
            i = 0
            while i < len(self.points):
                for p in points:
                    if p.Ve == self.points[i].Ve and p.Vn == self.points[i].Vn and p.lat == self.points[i].lat:
                        self.points.pop(i)
                        i-=1
                        break
                i+=1
            Clastrization.DISTANCE += 1
            arcpy.AddMessage("Added claster {}".format(i))
            if(len(self.points) < 15):
                break
            #self.claster.append(self.points)
        
            
        path = parameters[1].valueAsText # type: (str)
        arcpy.AddMessage(path)
        arcpy.AddMessage(parameters[1].valueAsText)
        name = re.search(string=path,pattern="[\w-]+\.shp")
        name = name.group(0)
        arcpy.AddMessage(name)
        arcpy.AddMessage(arcpy.Describe(parameters[0]).SpatialReference.name)
        # Create a new point shapefile
        arcpy.CreateFeatureclass_management(out_path=path[:len(path) - len(name)],out_name=name,geometry_type="POINT",template=parameters[0].value)


        # Set the desired spatial reference using a well-known ID (WKID)
        spatial_reference = arcpy.Describe(parameters[0]).SpatialReference # Example: WGS84

        # Use DefineProjection_management to set the spatial reference
        arcpy.DefineProjection_management(name, spatial_reference)

                # TEXT—The field type will be text. Text fields support a string of characters.
        # FLOAT—The field type will be float. Float fields support fractional numbers between -3.4E38 and 1.2E38.
        # DOUBLE—The field type will be double. Double fields support fractional numbers between -2.2E308 and 1.8E308.
        # SHORT—The field type will be short. Short fields support whole numbers between -32,768 and 32,767.
        # LONG—The field type will be long. Long fields support whole numbers between -2,147,483,648 and 2,147,483,647.
        # DATE—The field type will be date. Date fields support date and time values.
        # BLOB—The field type will be BLOB. BLOB fields support data stored as a long sequence of binary numbers. You need a custom loader or viewer or a third-party application to load items into a BLOB field or view the contents of a BLOB field.
        # RASTER—The field type will be raster. Raster fields can store raster data in or alongside the geodatabase. All ArcGIS software-supported raster dataset formats can be stored, but it is recommended that only small images be used.
        # GUID—The field type will be GUID. GUID fields store registry-style strings consisting of 36 characters enclosed in curly brackets.
        # Add fields to the shapefile
        arcpy.AddField_management(path, "Claster_id", "SHORT")
        arcpy.AddField_management(path, "Ve", "DOUBLE")
        arcpy.AddField_management(path, "Vn", "DOUBLE")
        arcpy.AddField_management(path, "Bearing", "DOUBLE")
        

        # Open an insert cursor to add data to the shapefile
        cursor = arcpy.da.InsertCursor(path, ["SHAPE@","lat","long", "Claster_id", "Ve","Vn","Bearing"])

        i = 0

        for c in self.claster:
            i+=1
            for p in c:
                # Add points to the shapefile
                point1 = arcpy.Point(p.lat, p.long)
                cursor.insertRow([point1, p.lat, p.long, i, p.Ve, p.Vn,calculate_bearing(p.Ve,p.Vn)])


        # Delete the cursor
        del cursor

        # Refresh the map view to see the added shapefile
        arcpy.RefreshActiveView()

        return
