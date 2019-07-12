# -*- coding: utf-8 -*-
import random,time,json
import numpy as np 

class Point():
    x=0
    y=0
    def __init__(self,x=0,y=0):
        self.x=int(x)
        self.y=int(y)
    def move(self,_direction):
        self.y+=int(_direction[0])
        self.x+=int(_direction[1])
    def distance(self,pt1,pt2):
        return abs(pt1.x-pt2.x)+abs(pt1.y-pt2.y)
    def isNeighbor(self,pt1,pt2):
        if abs(pt1.x-pt2.x)<=1 and abs(pt1.y-pt2.y)<=1:
            return True
        return False 
    def __str__(self):
        return "<(y,x)=({},{})>".format(self.y,self.x)

role = {"NULL":0, "BLACK":1, "WHITE":2}
direc = {"U":(-1,0),"UR":(-1,1),"R":(0,1),"DR":(1,1),"D":(1,0),"DL":(1,-1),"L":(0,-1),"UL":(-1,-1)}

PLAYER = [role["BLACK"], role["WHITE"]]
def next_player( turn=PLAYER[0] ):
    if PLAYER.index( turn ) == 0 :
        return PLAYER[1]
    return PLAYER[0]

class Board(object):
        
    def __init__(self, width=8, height=8 , _board=None):
        self.width = width
        self.height = height

        if _board is None:
            self.board = np.array( [role["NULL"] for i in range(width*height)] )
            self.board = np.reshape(self.board, (height,width))
                        
            for i in range(1,width-1):
                self.board[0][i] = role["BLACK"]
                self.board[height-1][i] = role["BLACK"]

            for i in range(1,height-1):
                self.board[i][0] = role["WHITE"]
                self.board[i][width-1] = role["WHITE"]
                
        else:
            self.board = np.copy(_board)
            
        self.countWht = 0
        self.countBlk = 0
        
    def graph(self):
        width = self.width
        height = self.height
        board = self.board
 
        for i in range(width):
            print("{0:8}".format(i), end='')
        print("\r\n")
        
        for i in range(height):
            print("{0:4d}".format(i), end='')
            for j in range(width):
                if(board[i][j]==role["NULL"]):
                    print('_'.center(8), end='')
                elif(board[i][j]==role["WHITE"]):
                    print('W'.center(8), end='')
                elif(board[i][j]==role["BLACK"]):
                    print('B'.center(8), end='')
            print('\r\n\r\n')
        print(' countBlk:',self.countBlk,' countWht:',self.countWht)
        
    def count_chess_on_dir(self,_role,_point,_direction):
        width = self.width
        height = self.height
        board = self.board
        if type(_point) is tuple or type(_point) is list :
            _point = Point(y=_point[0],x=_point[1])

        countChess=1
        # 往_direction方向計算路上棋子數量
        pointMove = Point(y=_point.y,x=_point.x)
        pointMove.move(_direction)
        while(pointMove.x>=0 and pointMove.x<width and pointMove.y>=0 and pointMove.y<height):
            if board[pointMove.y][pointMove.x] != role["NULL"]:
                countChess+=1
            pointMove.move(_direction)
        # 往反_direction方向計算路上棋子數量
        _directionInv = (-_direction[0],-_direction[1])
        pointMove = Point(y=_point.y,x=_point.x)
        pointMove.move(_directionInv)
        while(pointMove.x>=0 and pointMove.x<width and pointMove.y>=0 and pointMove.y<height):
            if board[pointMove.y][pointMove.x] != role["NULL"]:
                countChess+=1
            pointMove.move(_directionInv)

        return countChess
        
    def canMove(self,_role,_point,_direction):
        width = self.width
        height = self.height
        board = self.board

        # 計算 direction 方向上的棋子數量
        countChess = self.count_chess_on_dir(_role,_point,_direction)

        # 看那格是否還在棋盤中
        pointMove = Point(x=_point.x+countChess*_direction[1],y=_point.y+countChess*_direction[0])
        if pointMove.x<0 or pointMove.x>width-1 or pointMove.y<0 or pointMove.y>height-1 :
            return False
        pointMove = Point(x=_point.x, y=_point.y)
        
        # 看看路上是否有敵方的棋子
        for i in range(countChess-1):
            pointMove.move(_direction)
            if board[ pointMove.y ][ pointMove.x ] != _role and board[ pointMove.y ][ pointMove.x ] != role["NULL"] :
                return False
            
        # 判斷dstPoint是否已經有己方的棋子
        pointMove.move(_direction)
        if board[ pointMove.y ][ pointMove.x ] == _role :
            return False
        return True
        
    def available_actions(self,_role):
        width = self.width
        height = self.height
        board = self.board

        avaliActions = []

        for i in range(height):
            for j in range(width):
                if board[i][j] == _role:
                    pt = Point(y=i,x=j)
                    # 往8個方向探索
                    for direction in direc.values():
                        if self.canMove(_role,pt,direction) is True :
                            avaliActions.append({"role":_role,"point":[pt.y,pt.x],"direction":list(direction)})
        
        return avaliActions

    def can_make_action(self,_role):
        if len(self.available_actions(_role))>0 :
            return True
        return False

    def get_one_avaliAction_randomly(self,_role):
        avaliActions = self.available_actions(_role)
        if len(avaliActions) == 0 :
            return 0
        avaliAction = random.choices(avaliActions)[0]
        return avaliAction

    def has_winner(self):
        width = self.width
        height = self.height 
        board = self.board

        # 判斷一方只剩一個子，則另一方贏
        countBlk = countWht = 0
        for i in range(height):
            for j in range(width):
                if board[i][j] == role["BLACK"] :
                    countBlk+=1
                elif board[i][j] == role["WHITE"] :
                    countWht+=1
                    
        self.countWht = countWht
        self.countBlk = countBlk
        
        if countBlk <= 1:
            return True, role["WHITE"]
        elif countWht <= 1:
            return True, role["BLACK"]

        # 判斷是否有一方已經集結
        if self.isConnect(role["WHITE"]):
            return True, role["WHITE"]
        if self.isConnect(role["BLACK"]):
            return True, role["BLACK"]
        
        return False, role["NULL"]
        
    def isConnect(self, _role):
        width = self.width
        height = self.height
        board = self.board

        chestList = []
        groupList = []

        for i in range(height):
            for j in range(width):
                if board[i][j] == _role :
                    pt = Point()
                    pt.x = j
                    pt.y = i
                    chestList.append(pt)
        
        groupList.append(chestList[0])
        chestList.remove(chestList[0])
        while(True):
            needContinue=False 
            for gpPoint in groupList:
                for chPoint in chestList:
                    if Point().isNeighbor(gpPoint,chPoint) is True :
                        groupList.append(chPoint)
                        chestList.remove(chPoint)
                        needContinue=True 
            if(needContinue==False):
                break 

        if len(chestList)==0:
            return True
        return False 

    def make_action(self, _action):
        board = self.board
        if type(_action) is str :
            _action = json.loads(str(_action).replace("'",'"'))
            print("there is a action in string ERROR ")
            input()
        
        #{"role":_role,"point":(pt.y,pt.x),"direction":direction}
        _role = _action["role"]
        _point = _action["point"]
        _point = Point(y=_point[0],x=_point[1]) if type(_point) is list or type(_point) is tuple else None
        _direction = _action["direction"]

        if self.canMove(_role,_point,_direction) is False:
            print("\t[Info] Illegal Move\n")
            return False

        # 計算 direction 方向上的棋子數量，以及移動的位置
        countChess = self.count_chess_on_dir(_role,_point,_direction)
        
        pointSrc = _point
        pointDst = Point(x=_point.x+countChess*_direction[1],y=_point.y+countChess*_direction[0])

        # 更新棋盤
        board[pointDst.y][pointDst.x] = board[pointSrc.y][pointSrc.x]
        board[pointSrc.y][pointSrc.x] = role["NULL"]
        
        return True

    def countBlk_countWht(self):
        width = self.width
        height = self.height 
        board = self.board

        # 判斷一方只剩一個子，則另一方贏
        countBlk = countWht = 0
        for i in range(height):
            for j in range(width):
                if board[i][j] == role["BLACK"] :
                    countBlk+=1
                elif board[i][j] == role["WHITE"] :
                    countWht+=1
                    
        self.countWht = countWht
        self.countBlk = countBlk
        
    def set_board(self, _board=None):
        self.board = np.copy(_board)
        
    def get_board(self):
        return self.board



"""
board = Board()
board2 = Board()
while True :
    board.set_board(board2.get_board())
    abc = board.available_actions(role["BLACK"])
    ac = random.choices(abc)
    board.make_action(ac[0])
    board.graph()

    board2.set_board(board.get_board())
    abc = board2.available_actions(role["WHITE"])
    ac = random.choices(abc)
    board2.make_action(ac[0])
    board2.graph()

    hasWinner, Winner = board.has_winner()
    if hasWinner :
        print("winner:",Winner)
        break
"""


