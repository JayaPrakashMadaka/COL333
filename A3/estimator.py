import util
from util import*
from engine.const import Const
import time
import math
# Class: Estimator
#----------------------
# Maintain and update a belief distribution over the probability of a car being in a tile.

def getdist(x1,y1,x2,y2):
	return math.sqrt((x1-x2)*(x1-x2)+(y1-y2)*(y1-y2))

def getsum(l):
	sum=0
	for i in range(len(l)):
		for j in range(len(l[0])):
			sum+=l[i][j]
	return sum

class Estimator(object):
    def __init__(self, numRows: int, numCols: int):
        self.belief = util.Belief(numRows, numCols) 
        self.transProb = util.loadTransProb()
        self.particles = [[1 for i in range(numCols)] for j in range(numRows)]
            
    ##################################################################################
    # [ Estimation Problem ]
    # Function: estimate (update the belief about a StdCar based on its observedDist)
    # ----------------------
    # Takes |self.belief| -- an object of class Belief, defined in util.py --
    # and updates it *inplace* based onthe distance observation and your current position.
    #
    # - posX: x location of AutoCar 
    # - posY: y location of AutoCar 
    # - observedDist: current observed distance of the StdCar 
    # - isParked: indicates whether the StdCar is parked or moving. 
    #             If True then the StdCar remains parked at its initial position forever.
    # 
    # Notes:
    # - Carefully understand and make use of the utilities provided in util.py !
    # - Remember that although we have a grid environment but \
    #   the given AutoCar position (posX, posY) is absolute (pixel location in simulator window).
    #   You might need to map these positions to the nearest grid cell. See util.py for relevant methods.
    # - Use util.pdf to get the probability density corresponding to the observedDist.
    # - Note that the probability density need not lie in [0, 1] but that's fine, 
    #   you can use it as probability for this part without harm :)
    # - Do normalize self.belief after updating !!

    ###################################################################################
    def estimate(self, posX: float, posY: float, observedDist: float, isParked: bool) -> None:
        # BEGIN_YOUR_CODE

        # END_YOUR_CODE
        
        
        row = yToRow(posY)
        col = xToCol(posX)
        numCols = self.belief.getNumCols()
        numRows = self.belief.getNumRows()
        
        mat = self.belief.grid.copy()
        particles = [[0 for j in range(numCols)] for i in range(numRows)]
        
        for i in range(numRows):
        	for j in range(numCols):
        		particles[i][j]=int(mat[i][j]*1000000)
        		
        particles_new = particles
        
        for i in range(numRows):
        	for j in range(numCols):
        		dict={}
        		if(((i,j),(i,j)) in self.transProb ):
        			dict[(i,j),(i,j)] = self.transProb[(i,j),(i,j)]
        		if(((i,j),(i+1,j)) in self.transProb ):
        			dict[(i,j),(i+1,j)] = self.transProb[(i,j),(i+1,j)]
        		if(((i,j),(i-1,j)) in self.transProb ):
       				dict[(i,j),(i-1,j)] = self.transProb[(i,j),(i-1,j)]
       			if(((i,j),(i,j+1)) in self.transProb ):
       				dict[(i,j),(i,j+1)] = self.transProb[(i,j),(i,j+1)]
       			if(((i,j),(i,j-1)) in self.transProb ):
       				dict[(i,j),(i,j-1)] = self.transProb[(i,j),(i,j-1)]
       			if(((i,j),(i+1,j+1)) in self.transProb ):
       				dict[(i,j),(i+1,j+1)] = self.transProb[(i,j),(i+1,j+1)]
       			if(((i,j),(i-1,j-1)) in self.transProb ):
       				dict[(i,j),(i-1,j-1)] = self.transProb[(i,j),(i-1,j-1)]
       			if(((i,j),(i+1,j-1)) in self.transProb ):
       				dict[(i,j),(i+1,j-1)] = self.transProb[(i,j),(i+1,j-1)]
       			if(((i,j),(i-1,j+1)) in self.transProb ):
       				dict[(i,j),(i-1,j+1)] = self.transProb[(i,j),(i-1,j+1)]
       			
       			sorted_dict = sorted(dict.items(), key=lambda x:x[1],reverse=True)
       			
       			for key,value in sorted_dict:
       				if(particles[i][j]>0):
       					if(key[0]!=key[1]):
       						particles_new[key[1][0]][key[1][1]]+=value*particles[i][j]
       						particles_new[key[0][0]][key[0][1]]= max(0,particles_new[key[0][0]][key[0][1]]-value*particles[i][j])
       						particles[key[0][0]][key[0][1]]= max(0,particles_new[key[0][0]][key[0][1]]-value*particles[i][j])
        
        weights = [[0 for i in range(numCols)] for j in range(numRows)]
        
        for i in range(numRows):
       		for j in range(numCols):
        		wt = getdist(posX,posY,colToX(j),rowToY(i))
        		weights[i][j]=pdf(observedDist,Const.SONAR_STD,wt)
        		#weights[i][j]=1/abs(wt-observedDist)
        
        
        for i in range(numRows):
        	for j in range(numCols):
        		p=self.belief.getProb(i,j)
        		if(isParked):
        			self.belief.setProb(i,j,p*weights[i][j])
        		else:
        			self.belief.setProb(i,j,particles_new[i][j]*weights[i][j])
        		
        self.belief.normalize()
        return
  
    def getBelief(self) -> Belief:
        return self.belief

   
