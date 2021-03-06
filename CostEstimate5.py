#Plethora Coding Exercise
#A. Benjamin Falk

#PROBLEMS RIGHT NOW: 
#     Probably doesn't work for off axis (diagonal) curves #fixed (still need to test)
#     
#place .json file into memory
#syntax: where both userDirectory and filename are strings, editable in Main()
from collections import OrderedDict    
import math
import json 

#Place .json file into Memory and save important information
def PlaceIntoMemory(userDirectory, filename):
    with open(userDirectory+filename) as data_file:
        global data
        data = json.load(data_file, object_pairs_hook = OrderedDict)             #Had to serialize the .json file in order for later area calculation
    global EdgesArray
    EdgesArray =[]       
    for key in data['Edges']:
        EdgesArray.append(key)
    global numEdges
    numEdges = len(EdgesArray)
    
    global AllVerticesArray
    AllVerticesArray=[]
    for key in data['Vertices']:
        AllVerticesArray.append(key)
    global numVertices
    numVertices = len(AllVerticesArray) 

#Function to initialize the variables/lists/dictionaries I will use
def Initialize():                                                                # alot of globals since I made an intialize function
    global padding                                                               # instead of just declaring variables
    padding = .1
    global materialCost
    materialCost = .75
    global maxSpeed
    maxSpeed = .5
    global cuttingTimeCost
    cuttingTimeCost = .07
    global straightCuttingCost
    straightCuttingCost = 0
    global arcCuttingCost
    arcCuttingCost = 0
    global addedArea
    addedArea = 0
    arcInside = False
    straightedgeVertices = {}
    arcedgeVertices = {}
 
#Store Edges as objects for easy access of their properties   
class Edge(object):
    def __init__(self,EdgeId,EdgeType):
        self.EdgeID = EdgeId
        self.EdgeType = EdgeType
    def isArc(self,EdgeType):
        if EdgeType == "LineSegment":
            return False
        else:
            return True       
    def getVertices(self):
        return data['Edges'][self.EdgeID]['Vertices'] 
    def getArcDirection(self):
        return data['Edges'][self.EdgeID]['ClockwiseFrom']
    
#Store Vertices as object to retrieve coordinates easier
class Vertice(object):   
    def __init__(self,VerticeID):
        self.VerticeID = VerticeID    
    def getXcoord(self):
        return data['Vertices'][self.VerticeID]['Position']['X']
    def getYcoord(self):
        return data['Vertices'][self.VerticeID]['Position']['Y']

#Function to Find all distances, straight or otherwise and calculate costs for cutting    
def FindDistances():   
    for i in range(numEdges):
        myEdge = Edge(EdgesArray[i],data['Edges'][EdgesArray[i]]['Type'])
        if myEdge.isArc(myEdge.EdgeType) == False:
            global straightedgeVertices
            straightedgeVertices = {'x1': data['Vertices'][str(myEdge.getVertices()[0])]['Position']['X'], 
                      'y1': data['Vertices'][str(myEdge.getVertices()[0])]['Position']['Y'], 
                      'x2': data['Vertices'][str(myEdge.getVertices()[1])]['Position']['X'],
                      'y2': data['Vertices'][str(myEdge.getVertices()[1])]['Position']['Y']}
            straightdistance = math.sqrt((straightedgeVertices['x2']-straightedgeVertices['x1'])**2 + (straightedgeVertices['y2'] - straightedgeVertices['y1'])**2)
            global straightCuttingCost
            straightCuttingCost += (straightdistance/maxSpeed)*cuttingTimeCost   #calculate cost of cutting a straight edge
        else:
            global arcedgeVertices
            arcedgeVertices = {'x1': data['Vertices'][str(myEdge.getVertices()[0])]['Position']['X'], 
                      'y1': data['Vertices'][str(myEdge.getVertices()[0])]['Position']['Y'], 
                      'x2': data['Vertices'][str(myEdge.getVertices()[1])]['Position']['X'],
                      'y2': data['Vertices'][str(myEdge.getVertices()[1])]['Position']['Y']}
            global radius                                                        #radius will be half the dist from arcvertex1 to arcvertex2
                                                                                 #no need for Edge Center method?
            radius = math.sqrt((arcedgeVertices['x2']-arcedgeVertices['x1'])**2 + (arcedgeVertices['y2'] - arcedgeVertices['y1'])**2)/2 

            arcDirectionVertice = {'x': data['Vertices'][str(myEdge.getArcDirection())]['Position']['X'],
                        'y': data['Vertices'][str(myEdge.getArcDirection())]['Position']['Y']}

            if myEdge.getVertices()[0] == myEdge.getArcDirection():              #if the Clockwise from vertex is the same as the 
                arcInside = True                                                 #first vertex of the curve, the arc will be cut not extruded
            else:
                arcInside = False

            if arcInside == False:
                global addedArea                                                 #added area to account for an extruded arc
                addedArea += radius * ((radius*2)+padding)                       #assuming the arcs must go from vertex to vertex not in between vertices      
            arcdistance = radius*math.pi
            arcCuttingSpeed = maxSpeed*math.exp(-1/radius)
            global arcCuttingCost                                                #calculate cost of cutting an arc
            arcCuttingCost += (arcdistance/arcCuttingSpeed)*cuttingTimeCost
#function used to calculate the Initial Area of any regular or irregular polygon, so long as the points are in order            
def FindArea(X,Y,numPoints):
    area = 0
    j = numPoints-1
    for i in range(numPoints):
        area += (X[j]+X[i])*(Y[j]-Y[i])
        j = i
    if area < 0:
        return area/-2                                                           # -2 or 2 based on whether the points in coordinate 
    else:                                                                        # lists are in clockwise or counterclockwise order
        return area/2
    
def Main():
    myDirectory = 'C:\\Users\\falka\\python files\\'                             #to change directory (must be string)
    filename = 'HexagonInnerArc.json'                                              #to change file (must be string)
    PlaceIntoMemory(myDirectory,filename) 
    Initialize()
    FindDistances()
    Xcoords=[]
    Ycoords=[]
    for i in range(numVertices):                                                 #save XY coords into lists
        MyVertice = Vertice(AllVerticesArray[i])
        Xcoords.append(MyVertice.getXcoord())
        Ycoords.append(MyVertice.getYcoord())
    
    for i in range(numVertices):
        if Xcoords[i] != 0:
            Xcoords[i] += padding                                                #for padding
        if Ycoords[i] != 0:
            Ycoords[i] += padding                                                #for padding
            
    iniArea = FindArea(Xcoords,Ycoords,numVertices)
    finalArea = iniArea+addedArea
    Areacost = finalArea*materialCost
    finalCost = Areacost+straightCuttingCost+arcCuttingCost
    print("%.2f" %finalCost + " dollars")                                        #answer rounded to 2 decimal places
        
Main()
