# -*- coding: utf-8 -*-

import os
dir_path = os.path.dirname(os.path.realpath(__file__))
import sys
import json
import math
import random
import numpy as np
import requests
from concurrent.futures import ThreadPoolExecutor,ProcessPoolExecutor

from state import *

class Node(object):
    """
    蒙地卡羅樹節點
    """
    def __init__(self,_state,_parent=None):
        self.parent = _parent
        self.children = []

        self.visitCount = 0
        self.qualityCount = 0

        self.state = _state

    def node_string(self, ID, childNodeIDs):
        dict_ = {"ID":ID, "children":childNodeIDs, "visitCount":self.visitCount, "qualityCount":self.qualityCount }

        return str(json.dumps(dict_)) , str(self.state.state_string(ID))

    def load_node_from_string(self, string):
        string = str(string)
        dict_ = json.loads(string)

        self.children = list( dict_["children"] )
        self.visitCount = int(dict_["visitCount"])
        self.qualityCount = int(dict_["qualityCount"])
        
    def add_child(self,_node):
        self.children.append(_node)
            
    def get_state(self):
        return self.state

    def get_parent(self):
        return self.parent

    def get_children(self):
        return self.children

    def get_a_child_randomly(self):
        child = random.choices( self.get_childen() )[0]
        return child
    
    def get_childNode_by_action(self,_action):
        # 如果childNode有被explore過
        for childNode in self.children :
            if childNode.get_state().get_action() == _action :
                return childNode
            
        # 如果childNode還沒被explore過
        childState = self.get_state().new_state_from_action( _action )
        childNode = Node( childState, self )
        self.children.append(childNode)
        
        return childNode

    def visitCount_add_one(self):
        self.visitCount += 1

    def qualityCount_add_one(self):
        self.qualityCount += 1

    def quality_value(self):
        return float(self.qualityCount/self.visitCount)

    def get_visitCount(self):
        return self.visitCount

    def get_qualityCount(self):
        return self.qualityCount


COMPUTE_BUDGET = 150

class Monte_Carlo_Tree_Search(object):
    """
    蒙地卡羅樹，4個步驟implement
    """
    def __init__(self):
        self.rootNode = None
        pass

    def UCTSearch(self,_rootNode):
        if self.rootNode is None :
            self.rootNode = _rootNode
        
        for i in range(COMPUTE_BUDGET):
            
            expandedNode = self.tree_policy( _rootNode )    # Tree policy

            winner = self.default_policy( expandedNode )    # Default policy

            self.back_up( expandedNode, winner )  # Back up

        return True

    def tree_policy(self, _node):
        # 隨機探索未知的子節點，如果探索完畢就選擇一個最好的子節點
        while _node.get_state().is_not_terminal()  :
            if _node.get_state().is_fully_expanded() is False :
                return self.expand( _node )
            else :
                _node = self.best_child( _node )

        return _node

    def best_child(self,_node,is_exploration=True):
        """
        exploration : 探勘未發現的
        exploitation : 探勘已發現的
        """
        if is_exploration: 
            C = 1 / math.sqrt(2.0)  # UCB 算法 平衡各節點探勘數量
        else:
            C = 0.0 # 純粹找出最好的子節點

        bestChildNode = None
        bestScore = -1000
        for subNode in _node.get_children() :
            score = self.UCB(subNode, C)
            if score > bestScore :
                bestScore = score
                bestChildNode = subNode

        return bestChildNode
        
    def UCB(self,_node,_C=0):
        if _node.get_visitCount() == 0:
            _node.visitCount_add_one()
        left = (float) ( _node.quality_value() )
        right = (float) ( _C*math.sqrt( 2.0*math.log( (float) (_node.parent.get_visitCount())/_node.get_visitCount() ) ) )
        return left+right
    
    def expand(self,_node):
        # 隨機選擇新的state
        newState = _node.get_state().random_new_state_from_notExpandedAction()

        # 創子節點
        subNode = Node( _state=newState , _parent=_node )
        _node.add_child( subNode )
                
        return subNode
        
    def back_up(self,_node,_winner=PLAYER[0]):
        while _node!=None :
            """
            如果此節點turn(做選擇決定下一步)的跟最後勝利的人不一樣
            代表上一步做決定的就是最後勝利者
            此節點是好的節點
            那麼此節點的 qualityCount 就需要+1
            """
            if _node.parent!=None and _node.parent.get_state().get_turn() == _winner :
                _node.qualityCount_add_one()
                _node.visitCount_add_one()
            else : 
                _node.visitCount_add_one()
            # 往根結點傳播
            _node = _node.parent

    def default_policy(self,_node):

        turn = _node.get_state().get_turn()
        boardClass = Board( _board=1 )
        boardClass.set_board( _node.get_state().get_board() )
        isTerminal = boardClass.has_winner()
        
        while isTerminal[0] is False :
            randomAvaliAction = 0
            while randomAvaliAction == 0 :
                turn = next_player(turn)
                randomAvaliAction = boardClass.get_one_avaliAction_randomly( _role=turn )
            boardClass.make_action( randomAvaliAction )
            isTerminal = boardClass.has_winner()            

        return isTerminal[1]

    def load(self,_path="/model/"):
        nodeList = {}
        stateList = {}
        
        # read states
        print("\t[Info] loading mcts model : states")
        total_lines = sum(1 for line in open(dir_path+_path+"states"))
        load_lines = 1
        with open( dir_path+_path+"states", 'r') as f :
            line = f.readline()
            while line :
                st = json.loads( line )

                state = State()
                state.load_state_from_string( line )
                stateList[st["ID"]] = state
                
                line = f.readline()

                if load_lines%10000==0:
                    os.system('cls' if os.name == 'nt' else 'clear')
                    print("\t[Info] loading mcts model : states")
                    print("\t\t load states ",float(load_lines/total_lines),"%")
                load_lines += 1
        print("\t[Info] load mcts model : states, complete!!")
            
        # read nodes
        print("\t[Info] loading mcts model : nodes")
        total_lines = sum(1 for line in open(dir_path+_path+"nodes"))
        load_lines = 1
        with open( dir_path+_path+"nodes", 'r') as f :
            line = f.readline()
            while line :
                nd = json.loads( line )
                
                node = Node( stateList[nd["ID"]] )
                node.load_node_from_string( line )
                nodeList[nd["ID"]] = node
                
                line = f.readline()

                if load_lines%10000==0:
                    os.system('cls' if os.name == 'nt' else 'clear')
                    print("\t[Info] loading mcts model : nodes")
                    print("\t\t load nodes ",float(load_lines/total_lines),"%")
                load_lines += 1
        print("\t[Info] load mcts model : nodes, complete!!")

        # link : parent & children
        for nd in nodeList.values() :
            childIDs = nd.get_children()
            nd.children = []
            for id_ in childIDs :
                nd.children.append( nodeList[id_] )
                nodeList[id_].parent = nd

        # find rootNode
        for nd in nodeList.values() :
            if nd.parent == None :
                self.rootNode = nd
                break

        return self.rootNode
        
    def save(self,_path="/model/"):
        open( dir_path+_path+"nodes",'w').close() #清空nodes model
        open( dir_path+_path+"states",'w').close() #清空states model
        
        rootNode = self.rootNode
        nodePt = rootNode
    
        self.f_n = open( dir_path+_path+"nodes", 'a')
        self.f_s = open( dir_path+_path+"states", 'a')
        
        self.IDcount = 0
        self.dfs_save(rootNode, _path)

        self.f_s.close()
        self.f_n.close()
        
    def dfs_save(self, _node, _path="/model/"):
        childNodes = _node.get_children()
        childNodesIDs = []
        
        for childNode in childNodes :
            childNodesIDs.append( self.dfs_save(childNode) )
            
        self.IDcount += 1
        nodeString,stateString = _node.node_string( self.IDcount, childNodesIDs)
        print(nodeString, file=self.f_n)
        print(stateString, file=self.f_s)
            
        return self.IDcount
        
"""

########### 電腦vs隨機 ###############
randomRole = turn = role["BLACK"]

boardClassTmp = Board()

loadModel = True

if loadModel :
    mcts = Monte_Carlo_Tree_Search()
    nodePt = mcts.load()
else :
    rootState = State( _roundIdx=0, _availActions=boardClassTmp.available_actions( turn ), _board=boardClassTmp.get_board(), _turn=randomRole )
    rootNode = Node( _state=rootState )
    nodePt = rootNode

    mcts = Monte_Carlo_Tree_Search()
    mcts.UCTSearch( _rootNode=rootNode )

record = []
for ithSim in range(500):
    print("\n\t[Info] 第",ithSim,"盤模擬棋子")
    boardClassTmp = Board()
    nodePt = mcts.rootNode
    _iter=0
    while True :
        # 隨機下
        randomAction = boardClassTmp.get_one_avaliAction_randomly( _role=randomRole )
        if randomAction != 0 :
            boardClassTmp.make_action( randomAction )
            os.system('cls' if os.name == 'nt' else 'clear')
            _iter+=1
            print("\n\n第:",ithSim,"  iteration : ",_iter)
            print("[Info] ",randomAction)
            boardClassTmp.graph()

            # find node of randomAct
            nodePt = nodePt.get_childNode_by_action( randomAction )
            mcts.UCTSearch( _rootNode=nodePt )
            
        if boardClassTmp.has_winner()[0] is True :
            break
        
        # 換電腦下
        turn = next_player( randomRole )
        if len(boardClassTmp.available_actions( turn ))==0:
            turn = next_player( turn )
            continue
        
        bestChildNode = mcts.best_child(nodePt,is_exploration=False)
        bestAction = bestChildNode.get_state().get_action()
        if bestAction != 0 :
            boardClassTmp.make_action( bestAction )
            os.system('cls' if os.name == 'nt' else 'clear')
            _iter+=1
            print("\n\n第:",ithSim,"  iteration : ",_iter)
            print("[Info] ",bestAction)
            boardClassTmp.graph()

        nodePt = bestChildNode
        
        if boardClassTmp.has_winner()[0] is True :
            break

    record.append( boardClassTmp.has_winner() )
    print( boardClassTmp.has_winner() )
    
mcts.save()
print(record)

########### AI vs 隨機 ###############

"""

"""

########### AI vs AI ###############

boardClassTmp = Board()

loadModel = True
if loadModel :
    mcts = Monte_Carlo_Tree_Search()
    nodePt = mcts.load()
else :
    rootState = State( _roundIdx=0, _availActions=boardClassTmp.available_actions( turn ), _board=boardClassTmp.get_board(), _turn=randomRole )
    rootNode = Node( _state=rootState )
    nodePt = rootNode

    mcts = Monte_Carlo_Tree_Search()
    mcts.UCTSearch( _rootNode=rootNode )

record = []
for ithSim in range(3):
    print("\n\t[Info] 第",ithSim,"盤模擬棋子")
    turn = role["BLACK"]
    boardClassTmp = Board()
    nodePt = mcts.rootNode
    _iter = 0
    while True :
        mcts.UCTSearch( _rootNode=nodePt )

        nodePt = mcts.best_child(nodePt,is_exploration=False)
        bestAction = nodePt.get_state().get_action()
        if bestAction != 0 :
            boardClassTmp.make_action( bestAction )
            os.system('cls' if os.name == 'nt' else 'clear')
            _iter+=1
            print("\n\n第:",ithSim,"  iteration : ",_iter)
            print("[Info] ",bestAction)
            boardClassTmp.graph()
            
        if boardClassTmp.has_winner()[0] is True :
            break

        # 如果對方有棋子可以下，那換對方下
        if boardClassTmp.can_make_action( next_player(turn) ) is True :
            turn = next_player( turn )

    record.append( boardClassTmp.has_winner() )
    print( boardClassTmp.has_winner() )

mcts.save()
print(record)

########### AI vs AI ###############
"""

