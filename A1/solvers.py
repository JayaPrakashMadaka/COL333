import json
import random
from queue import PriorityQueue
class SentenceCorrector(object):
    def __init__(self, cost_fn, conf_matrix):
        self.conf_matrix = conf_matrix
        self.cost_fn = cost_fn

        # You should keep updating following variable with best string so far.
        self.best_state = None 
	
    def search(self, start_state):
    	alpha_list=["a","b","c","d","e","f","g","h","i","j","k","l","m","n","o","p","q","r","s","t","u","v","w","x","y","z"]
    	correct_dict={}
    	for i in alpha_list:
    		correct_dict[i]=[]
    	for i in alpha_list:
    		for key in self.conf_matrix:
    			if(i in self.conf_matrix[key]):
    				correct_dict[i].append(key)
    	
    	k=10
    	best_states=[start_state]
    	while(True):
    		d={}
    		q=PriorityQueue()
    		for state in best_states:
    			d[self.cost_fn(state)]=state
    			q.put(-1*self.cost_fn(state))
    		for state in best_states:
    			j=0	
    			while(j<len(start_state)):
    				if(start_state[j]==' '):
    					j+=1
    				else:
    					for alpha in correct_dict[state[j]]:
    						newstate=state[0:j]+alpha+state[j+1:len(start_state)]
    						if(q.qsize()<k):
    							q.put(-1*self.cost_fn(newstate))
    							d[self.cost_fn(newstate)]=newstate
    						else:
    							x=q.get()
    							if(x<-1*self.cost_fn(newstate)):
    								q.put(-1*self.cost_fn(newstate))
    								d[self.cost_fn(newstate)]=newstate
    							else:
    								q.put(x)
    					j+=1
    		newbest_states=[]
    		while(q.qsize()>0):
    			newbest_states.append(d[-1*q.get()])
    		newbest_states.reverse()
    		best_states=newbest_states
    		self.best_state=newbest_states[0]
    	
    	self.best_state=best_states[0]
    			
    			
    			
    			
    			
    			
    			
    			
