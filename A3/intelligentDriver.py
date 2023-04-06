'''
Licensing Information: Please do not distribute or publish solutions to this
project. You are free to use and extend Driverless Car for educational
purposes. The Driverless Car project was developed at Stanford, primarily by
Chris Piech (piech@cs.stanford.edu). It was inspired by the Pacman projects.
'''
import util
import itertools
import math
from turtle import Vec2D
from engine.const import Const
from engine.vector import Vec2d
from engine.model.car.car import Car
from engine.model.layout import Layout
from engine.model.car.junior import Junior
from configparser import InterpolationMissingOptionError



def getsum(l):
	sum=0
	for i in range(len(l)):
		for j in range(len(l[0])):
			sum+=l[i][j]
	return sum


def getdist(x1,y1,x2,y2):
	return math.sqrt((x1-x2)*(x1-x2)+(y1-y2)*(y1-y2))

def getmap(n,m,blocks):
    matrix = [[0 for a in range(m+2)] for b in range(n+2)]
    for a in range(1,n+1):
        for b in range(1,m+1):
            matrix[a][b]=1
    for block in blocks:
        col1, row1, col2, row2 = block[0], block[1], block[2], block[3]
        row1 = row1+1
        row2 = row2+1
        col1 = col1+1
        col2 = col2+1
        if(row1 > 0):
            row1 = row1-1
        if(col1 > 0):
            col1 = col1-1
        if(row2<n):
            row2 = row2+1
        if(col2<m):
            col2 = col2+1
        for a in range(row1,row2):
            for b in range(col1,col2):
                matrix[a][b] = 0
                
    return matrix

def getactions(i,j,matrix):
    ans = []
    i = i + 1
    j = j + 1
    if(matrix[i][j] == 1):
        ans.append((i-1,j-1))
    if(matrix[i-1][j] == 1):
        ans.append((i-2,j-1))
    if(matrix[i+1][j] == 1):
        ans.append((i,j-1))
    if(matrix[i][j+1] == 1):
        ans.append((i-1,j))
    if(matrix[i-1][j+1] == 1):
        ans.append((i-2,j))
    if(matrix[i+1][j+1] == 1):
        ans.append((i,j))
    if(matrix[i][j-1] == 1):
        ans.append((i-1,j-2))
    if(matrix[i-1][j-1] == 1):
        ans.append((i-2,j-2))
    if(matrix[i+1][j-1] == 1):
        ans.append((i,j-2))
    return ans

#Shortest Path

class ShortestPath:
  def __init__(self, start, end , adj, nodes):
    self.start = start
    self.nodes=nodes
    self.adj = adj
    self.end = end
    self.prev = {}
  
  def bfs(self):
    visited ={}
    for node in self.nodes:
    	visited[node]=False
    queue = []
    visited[self.start] = True
    queue.append(self.start)
    while queue:
      current_node = queue.pop(0)
      for node in self.adj[current_node]:
        if not visited[node]:
          visited[node] = True
          queue.append(node)
          self.prev[node] = current_node
          if node == self.end:
            queue.clear()
            break;
    node = self.end
    route = []
    while (node in self.prev):
      route.append(node)
      node = self.prev[node]
    route.append(self.start)
    route.reverse()
    return route

# Class: Graph
# -------------
# Utility class
class Graph(object):
    def __init__(self, nodes, edges):
        self.nodes = nodes
        self.edges = edges
        
       	
       	
# Class: IntelligentDriver
# ---------------------
# An intelligent driver that avoids collisions while visiting the given goal locations (or checkpoints) sequentially. 
class IntelligentDriver(Junior):

    # Funciton: Init
    def __init__(self, layout: Layout):
        self.burnInIterations = 30
        self.layout = layout 
        # self.worldGraph = None
        self.worldGraph = self.createWorldGraph()
        self.checkPoints = self.layout.getCheckPoints() # a list of single tile locations corresponding to each checkpoint
        self.transProb = util.loadTransProb()
        
    # ONE POSSIBLE WAY OF REPRESENTING THE GRID WORLD. FEEL FREE TO CREATE YOUR OWN REPRESENTATION.
    # Function: Create World Graph
    # ---------------------
    # Using self.layout of IntelligentDriver, create a graph representing the given layout.
    def createWorldGraph(self):
        nodes = []
        edges = []
        numRows, numCols = self.layout.getBeliefRows(), self.layout.getBeliefCols()
        
        nodes = [(x, y) for x, y in itertools.product(range(numRows), range(numCols))]
        
        blocks = self.layout.getBlockData()
        blockTiles = []
        for block in blocks:
            row1, col1, row2, col2 = block[1], block[0], block[3], block[2] 
            # some padding to ensure the AutoCar doesn't crash into the blocks due to its size. (optional)
            row1, col1, row2, col2 = row1-1, col1-1, row2+1, col2+1
            blockWidth = col2-col1 
            blockHeight = row2-row1 

            for i in range(blockHeight):
                for j in range(blockWidth):
                    blockTile = (row1+i, col1+j)
                    blockTiles.append(blockTile)

        ## Remove blockTiles from 'nodes'
        nodes = [x for x in nodes if x not in blockTiles]

        for node in nodes:
            x, y = node[0], node[1]
            adjNodes = [(x, y-1), (x, y+1), (x-1, y), (x+1, y)]
            
            # only keep allowed (within boundary) adjacent nodes
            adjacentNodes = []
            for tile in adjNodes:
                if tile[0]>=0 and tile[1]>=0 and tile[0]<numRows and tile[1]<numCols:
                    if tile not in blockTiles:
                        adjacentNodes.append(tile)

            for tile in adjacentNodes:
                edges.append((node, tile))
                edges.append((tile, node))
        return Graph(nodes, edges)

    #######################################################################################
    # Function: Get Next Goal Position
    # ---------------------
    # Given the current belief about where other cars are and a graph of how
    # one can driver around the world, chose the next position.
    #######################################################################################
    def getNextGoalPos(self, beliefOfOtherCars: list, parkedCars:list , chkPtsSoFar: int):
        '''
        Input:
        - beliefOfOtherCars: list of beliefs corresponding to all cars
        - parkedCars: list of booleans representing which cars are parked
        - chkPtsSoFar: the number of checkpoints that have been visited so far 
                       Note that chkPtsSoFar will only be updated when the checkpoints are updated in sequential order!
        
        Output:
        - goalPos: The position of the next tile on the path to the next goal location.
        - moveForward: Unset this to make the AutoCar stop and wait.

        Notes:
        - You can explore some files "layout.py", "model.py", "controller.py", etc.
         to find some methods that might help in your implementation. 
        '''
        goalPos = (0, 0) # next tile 
        moveForward = True

        currPos = self.getPos() # the current 2D location of the AutoCar (refer util.py to convert it to tile (or grid cell) coordinate)
        # BEGIN_YOUR_CODE 

        # END_YOUR_CODE
        
        MIN_PROB = 0.1
        
        CAR_MIN_PROB = 0.02
        
        posX , posY = currPos
        
        gposX , gposY = self.checkPoints[chkPtsSoFar]
        
        
        row = util.yToRow(posY)
        col = util.xToCol(posX)
                
        numRows, numCols = self.layout.getBeliefRows(), self.layout.getBeliefCols()
        
        blocks = self.layout.getBlockData()
        
        map = getmap(numRows,numCols,blocks)
        
        for k in range(len(beliefOfOtherCars)):
        	if(parkedCars[k]):
        		for i in range(numRows):
        			for j in range(numCols):
        				if(beliefOfOtherCars[k].getProb(i,j)>CAR_MIN_PROB):
        					map[i+1][j+1]=0
        
        nodes = []
        for i in range(len(map)):
        	for j in range(len(map[0])):
        		if(map[i][j]==1):
        			nodes.append((i-1,j-1))
        			
        adj={}
        for node in nodes:
        	i,j = node
        	adj[node]=getactions(i,j,map)
        
        weight=[[0 for i in range(numCols)] for j in range(numRows)]
        
        for i in range(numRows):
        	for j in range(numCols):
        		for k in range(0,len(beliefOfOtherCars)):
        			if(parkedCars[k]==False):
        				weight[i][j]+=beliefOfOtherCars[k].getProb(i,j)
        
        sum = getsum(weight)
        
        for i in range(numRows):
        	for j in range(numCols):
        		if(sum!=0):
        			weight[i][j]=weight[i][j]/sum
        
        
        reward = [[0 for i in range(numCols)] for j in range(numRows)]
        
        for i in range(numRows):
        	for j in range(numCols):
        		if(map[i+1][j+1]==1):
        			paths = ShortestPath((i,j),(gposX,gposY),adj,nodes).bfs()
        			k=10
        			for tup in paths:
        				x,y = tup
        				reward[x][y]+=k
        				k+=10
        		else:
        			reward[i][j]=0
        
        
        sum1=getsum(reward)
        
        for i in range(numRows):
        	for j in range(numCols):
        		reward[i][j]=reward[i][j]/sum1
        	
        
        for i in range(numRows):
        	for j in range(numCols):
        		reward[i][j]-=2*weight[i][j]
        
        reward[gposX][gposY]=100
        
        actions = getactions(row,col,map)
        
        max_weight=0
        
        for a in actions:
        	i,j = a
        	max_weight=max(max_weight,weight[i][j])
        		
        if(max_weight>MIN_PROB):
        	moveForward=False
        
        max_action = (row,col)
        for action in actions:
        	max_row , max_col = max_action
        	i , j = action
        	if(reward[i][j]>reward[max_row][max_col]):
        		max_action = action
        
        max_row , max_col = max_action
        
        if(max_row == row and max_col == col):
        	moveForward = False
        
        goalPos = (util.colToX(max_col),util.rowToY(max_row))
        
        return goalPos, moveForward

    # DO NOT MODIFY THIS METHOD !
    # Function: Get Autonomous Actions
    # --------------------------------
    def getAutonomousActions(self, beliefOfOtherCars: list, parkedCars: list, chkPtsSoFar: int):
        # Don't start until after your burn in iterations have expired
        if self.burnInIterations > 0:
            self.burnInIterations -= 1
            return[]
       
        goalPos, df = self.getNextGoalPos(beliefOfOtherCars, parkedCars, chkPtsSoFar)
        vectorToGoal = goalPos - self.pos
        wheelAngle = -vectorToGoal.get_angle_between(self.dir)
        driveForward = df
        actions = {
            Car.TURN_WHEEL: wheelAngle
        }
        if driveForward:
            actions[Car.DRIVE_FORWARD] = 1.0
        return actions
    
    
