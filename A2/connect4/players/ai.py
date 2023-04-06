import random
import numpy as np
from typing import List, Tuple, Dict
from connect4.utils import get_pts, get_valid_actions, Integer
import time

def matrix(m,n):
    ans = []
    for i in range(m):
        ans.append([])
        for j in range(n):
            ans[i].append(0)
    if(m%2 == 0):
        a = m//2
    else:
        a = m//2 + 1
    if(n%2 == 0):
        b = n//2
    else:
        b = n//2 + 1
    for i in range(a):
        for j in range(b-1):
            ans[i][j] = i + (i+1)*j+3
        ans[i][b-1] = ans[i][b-2]+2
    for i in range(a):
        for j in range(b,n):
            ans[i][j] = ans[i][n-1-j]
    for i in range(a,m):
        for j in range(n):
            ans[i][j] = ans[m-1-i][j]
    return ans


class Node:
	def __init__(self,state : Tuple[np.array,Dict[int,Integer]],children,val,depth):
		self.state=state
		self.children=children
		self.val=val
		self.depth=depth
		
			

def get_state(state : Tuple[np.array,Dict[int,Integer]],player_number,action : Tuple[int,bool])->Tuple[np.array,Dict[int,Integer]]:
	col,pop=action
	board1,dict=state
	board=np.array(board1, copy=True)
	if(pop==False):
		arr=board[:,col]
		for i in range(len(arr)):
			if(arr[len(arr)-i-1]==0):
				arr[len(arr)-i-1]=player_number
				board[:,col]=arr
				break
		return (board,dict)
	elif(pop==True and dict[player_number].get_int()>0):
		arr=board[:,col]
		arr=np.delete(arr,len(arr)-1)
		arr=np.insert(arr,0,0)
		board[:,col]=arr
		dict[player_number].decrement()
		return (board,dict)
	else:
		return state


def heuristic(state : Tuple[np.array,Dict[int,Integer]],player_number1,player_number2):			
	board,dict=state
	mat=matrix(len(board),len(board[0]))
	val=0
	for i in range(len(mat)):
		for j in range(len(mat[0])):
			if(board[i][j]==player_number1):
				val+=mat[i][j]
			elif(board[i][j]==player_number2):
				val-=mat[i][j]
	return val

def heuristic1(state : Tuple[np.array,Dict[int,Integer]],player_number1,player_number2):
	board,dict=state
	return get_pts(player_number1,board)-get_pts(player_number2,board)




class AIPlayer:
    def __init__(self, player_number: int, time: int):
        """
        :param player_number: Current player number
        :param time: Time per move (seconds)
        """
        self.player_number = player_number
        self.type = 'ai'
        self.player_string = 'Player {}:ai'.format(player_number)
        self.time = time
        # Do the rest of your implementation here				
    
    def get_intelligent_move(self, state: Tuple[np.array, Dict[int, Integer]]) -> Tuple[int, bool]:
        """
        Given the current state of the board, return the next move
        This will play against either itself or a human player
        :param state: Contains:
                        1. board
                            - a numpy array containing the state of the board using the following encoding:
                            - the board maintains its same two dimensions
                                - row 0 is the top of the board and so is the last row filled
                            - spaces that are unoccupied are marked as 0
                            - spaces that are occupied by player 1 have a 1 in them
                            - spaces that are occupied by player 2 have a 2 in them
                        2. Dictionary of int to Integer. It will tell the remaining popout moves given a player
        :return: action (0 based index of the column and if it is a popout move)
        """
        # Do the rest of your implementation here
        root=Node(state,[],0,0)
        actions=get_valid_actions(self.player_number,state)
        depth=4
        d=0
        tree=[[root]]
        player1=self.player_number
        player2=0
        if(player1==1):
        	player2=2
        else:
        	player2=1
        while(d<depth):
        	lnew=[]
        	if(d%2==0):
        		for node in tree[-1]:
        			for a in get_valid_actions(player1,node.state):
        				new_state=get_state(node.state,player1,a)
        				child=Node(new_state,[],0,node.depth+1)
        				node.children.append(child)
        				lnew.append(child)
        		d+=1
        		tree.append(lnew)
        	else:
        		for node in tree[-1]:
        			for a in get_valid_actions(player2,node.state):
        				new_state=get_state(node.state,player2,a)
        				child=Node(new_state,[],0,node.depth+1)
        				node.children.append(child)
        				lnew.append(child)
        		d+=1
        		tree.append(lnew)
        
        for i in range(len(tree)):
        	layer=tree[len(tree)-i-1]
        	for node in layer:
        		if(len(node.children)==0):
        			node.val=heuristic(node.state,player1,player2)
        		elif(node.depth%2==0 and len(node.children)>0):
        			node.val=node.children[0].val
        			for child in node.children:
        				node.val=max(node.val,child.val)
        		elif(node.depth%2==1 and len(node.children)>0):
        			node.val=node.children[0].val
        			for child in node.children:
        				node.val=min(node.val,child.val)
        
        val=root.val
        for i in range(len(root.children)):
        	if(root.children[i].val==val):
        		return actions[i]
        return ()
        

    def get_expectimax_move(self, state: Tuple[np.array, Dict[int, Integer]]) -> Tuple[int, bool]:
        """
        Given the current state of the board, return the next move based on
        the Expecti max algorithm.
        This will play against the random player, who chooses any valid move
        with equal probability
        :param state: Contains:
                        1. board
                            - a numpy array containing the state of the board using the following encoding:
                            - the board maintains its same two dimensions
                                - row 0 is the top of the board and so is the last row filled
                            - spaces that are unoccupied are marked as 0
                            - spaces that are occupied by player 1 have a 1 in them
                            - spaces that are occupied by player 2 have a 2 in them
                        2. Dictionary of int to Integer. It will tell the remaining popout moves given a player
        :return: action (0 based index of the column and if it is a popout move)
        """
        root=Node(state,[],0,0)
        actions=get_valid_actions(self.player_number,state)
        depth=4
        d=0
        tree=[[root]]
        player1=self.player_number
        player2=0
        if(player1==1):
        	player2=2
        else:
        	player2=1
        while(d<depth):
        	lnew=[]
        	if(d%2==0):
        		for node in tree[-1]:
        			for a in get_valid_actions(player1,node.state):
        				new_state=get_state(node.state,player1,a)
        				child=Node(new_state,[],0,node.depth+1)
        				node.children.append(child)
        				lnew.append(child)
        		d+=1
        		tree.append(lnew)
        	else:
        		for node in tree[-1]:
        			for a in get_valid_actions(player2,node.state):
        				new_state=get_state(node.state,player2,a)
        				child=Node(new_state,[],0,node.depth+1)
        				node.children.append(child)
        				lnew.append(child)
        		d+=1
        		tree.append(lnew)
        
        for i in range(len(tree)):
        	layer=tree[len(tree)-i-1]
        	for node in layer:
        		if(len(node.children)==0):
        			node.val=heuristic(node.state,player1,player2)
        		elif(node.depth%2==0 and len(node.children)>0):
        			node.val=node.children[0].val
        			for child in node.children:
        				node.val=max(node.val,child.val)
        		elif(node.depth%2==1 and len(node.children)>0):
        			node.val=0
        			for child in node.children:
        				node.val+=child.val
        			node.val/=len(node.children)
        
        val=root.val
        for i in range(len(root.children)):
        	if(root.children[i].val==val):
        		return actions[i]
        return ()
