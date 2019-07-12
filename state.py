# -*- coding: utf-8 -*-

import json
import random
import numpy as np

from board import *

class State(object):

    def __init__(self,_roundIdx=0,_availActions=[],_action=None,_board=np.array([]),_turn=PLAYER[0]):
        self.roundIdx = _roundIdx
        self.turn = _turn

        self.availActions = _availActions.copy()
        self.notExpandedActions = _availActions.copy()
      
        self.action = _action   # 做了甚麼_action導致這個state,board
        self.board = np.copy(_board)

    def state_string(self, ID):
        dict_ = {"ID":ID, "roundIdx":self.roundIdx, "turn":self.turn, "availActions":self.availActions, "notExpandedActions":self.notExpandedActions,
                             "action":self.action, "board":self.board.tolist()}

        if self.action is None :
            dict_["action"] = 0
            
        return str(json.dumps(dict_))

    def load_state_from_string(self, string):
        string = str(string)
        dict_ = json.loads( string )

        self.roundIdx = dict_["roundIdx"]
        self.turn = dict_["turn"]
        self.availActions = list(dict_["availActions"])
        self.notExpandedActions = list(dict_["notExpandedActions"])
        if dict_["action"] == 0 :
            self.action = None
        else:
            self.action = json.loads(str(dict_["action"]).replace("'",'"'))
        self.board = np.array( dict_["board"] )
        
    def get_board(self):
        return np.copy(self.board)

    def get_action(self):
        return self.action
    
    def get_roundIdx(self):
        return self.roundIdx

    def get_turn(self):
        return self.turn
    
    def is_fully_expanded(self):
        return len(self.notExpandedActions)==0

    def is_not_terminal(self):
        return len(self.availActions)!=0
    
    def get_notExpandedActions(self):
        return self.notExpandedActions
    
    def remove_action_from_notExpandedActions(self,_action):
        self.notExpandedActions.remove(_action)

    def random_new_state_from_notExpandedAction(self):

        # 隨機選擇還沒找過的動作
        randomSelectedAction = random.choices(self.get_notExpandedActions())[0]

        # 模擬下棋動作，找到新的棋譜
        boardClass = Board( _board=1 )
        boardClass.set_board(self.get_board())
        boardClass.make_action(randomSelectedAction)
        
        # 新的state
        board = boardClass.get_board()
        availActions = boardClass.available_actions( next_player(self.get_turn()) )        
        
        if len(availActions) > 0 :
            # 如果敵方有棋子可走
            newState = State( _roundIdx=self.get_roundIdx()+1, _availActions=availActions,
                          _action=randomSelectedAction, _board=board, _turn=next_player(self.get_turn()))
        else :
            # 如果敵方沒棋子可下，那麼己方在走一次
            availActions = boardClass.available_actions( self.get_turn() )
            newState = State( _roundIdx=self.get_roundIdx()+1, _availActions=availActions,
                          _action=randomSelectedAction, _board=board, _turn=self.get_turn())
            if len(availActions) == 0 :
                print("\n\t[Info] 兩方都無棋子可走")
                exit(-1)

        self.remove_action_from_notExpandedActions(randomSelectedAction)

        return newState

    def new_state_from_action(self, _action):

        if _action not in self.availActions :
            print("\n\t[Error] Not Illegal Action")
        
        # 模擬下棋動作，找到新的棋譜
        boardClass = Board( _board=1 )
        boardClass.set_board(self.get_board())
        boardClass.make_action( _action )
        board = boardClass.get_board()
        availActions = boardClass.available_actions( next_player(self.get_turn()) )   
        
        newState = State( _roundIdx=self.get_roundIdx()+1, _availActions=availActions,
                        _action=_action, _board=board, _turn=next_player(self.get_turn()))
        self.remove_action_from_notExpandedActions( _action )
        
        return newState
        
    def get_availActions(self):
        return self.availActions

    def __eq__(self,_state2):
        if self.board == _state2.board :
            return True
        return False
