# miniAlphaGo-Monte_Carlo_Tree_Search-line_of_action
###### tags: `AI` `zju`
 [人工智能] 期中專題 miniAlphaGo 蒙地卡羅數搜索-集結棋

## 蒙地卡羅樹搜索演算法
### 4Step: (Selection、Expansion、Simulation、Backpropagation)
![](https://i.imgur.com/5dtq5op.png)
![](https://i.imgur.com/9DrifcO.png)
![](https://i.imgur.com/kMW4eDI.png)
![](https://i.imgur.com/XAZTemY.png)
![](https://i.imgur.com/DabvDXd.png)
### Upper Confidence Bounds on Trees (UCT)
![](https://i.imgur.com/q6CzcMT.png)
![](https://i.imgur.com/Y7zseJH.png)
### UCT Algorithm
![](https://i.imgur.com/7qQMSV0.png)

## 程式架構
```cmd=
使用語言: Python, Html Css Js
Python venv: Python 3.6.5
後端架構: Django
前端架構: Bootstrap Jquery
使用平台: Windows , Ubuntu
```
![](https://i.imgur.com/mSwVYtB.png)

## Model
![](https://i.imgur.com/V6th3P3.png)
```cmd=
model: 解壓縮model.zip，會有已經對弈過1000盤的蒙地卡羅樹，約3GB
model_sim: 輕量的model，約3MB
```

## 運行方式
1. Windows:
![](https://i.imgur.com/jppOknQ.png)
2. Ubuntu:
![](https://i.imgur.com/8w15RIG.png)
### 選擇model
![](https://i.imgur.com/vyfkaGF.png)
```cmd=
[1] light weight model:
    電腦vs電腦對弈過30盤棋，搜索過的蒙地卡羅樹。
[2] full model:
    電腦vs電腦對弈過超過1000盤棋，搜索過的蒙地卡羅樹。
    此model共3G，Load此model需要較長的時間，大約5~10分鐘，目前此full model
    有超過百萬個已走過的節點。
```
### 成功運行畫面
![](https://i.imgur.com/d9T1xBs.png)

↓ 接著在瀏覽器打開: http://localhost:8000
![](https://i.imgur.com/59tLrpQ.png)

↓ 按 [F12] 開啟瀏覽器console可以看到所有下棋動作，如果有error訊息也會在這裡顯示。
![](https://i.imgur.com/Owdz6jV.png)

↓ 後臺畫面應該會跟瀏覽器的一樣。
![](https://i.imgur.com/vZoFCgW.png)

## GUI(介面操作)
![](https://i.imgur.com/FQC5RTK.png)
### 1. 兩個玩家對弈
↓ 確認兩個AI操作都是OFF的狀態
![](https://i.imgur.com/ydLr26C.png)
↓ 點選想要移動的棋子，橘色格子為合法移動的位置，接著點選想要移動到的位置。
![](https://i.imgur.com/vCiAhv3.png)
### 2. 玩家、電腦對弈
↓ 確認Black AI OFF跟White AI ON的模式，即玩家是黑色棋子，電腦是白色棋子。
![](https://i.imgur.com/zNu5HIx.png)
↓ 電腦有1分鐘的思考時間，電腦會做蒙地卡羅樹搜索，須耐心等候。
![](https://i.imgur.com/BCoA1YH.png)
### 3. 電腦、電腦對弈
↓ 確認兩個AI操作都是ON的狀態
![](https://i.imgur.com/MassM0e.png)

## 蒙地卡羅樹搜索效果
![](https://i.imgur.com/Xw8Cd6U.png)
```cmd=
可以看到白色棋漸漸聚集起來，最後白色的棋贏了。
```

## 核心代碼
![](https://i.imgur.com/sjGCkq8.png)
### Class:Board
```python=
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
```
負責棋譜的正確性，以及動作的合法性，以及輸贏的判斷。
### Class:State
```python=
class State(object):

    def __init__(self,_roundIdx=0,_availActions=[],_action=None,_board=np.array([]),_turn=PLAYER[0]):
        self.roundIdx = _roundIdx
        self.turn = _turn

        self.availActions = _availActions.copy()
        self.notExpandedActions = _availActions.copy()
      
        self.action = _action   # 做了甚麼_action導致這個state,board
        self.board = np.copy(_board)
```
儲存棋譜，以及處存做了甚麼動作導致此state，以及換哪一方下棋，以及此state的所有合法動作
### Class:Node
```python=
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
```
存有一個state，並保存parent、children的指標，同時記錄visitCount、qualityCount。
### Class:Monte_Carlo_Tree_Search
#### A. 參數
```python=
class Monte_Carlo_Tree_Search(object):
    """
    蒙地卡羅樹，4個步驟implement
    """
    def __init__(self):
        self.rootNode = None
        pass
```
self.rootNode是整個蒙地卡羅樹最上面的那個點。
#### B. Computation budget
![](https://i.imgur.com/VplNnTO.png)
COMPUTE_BUDGET=150，每次做UCTSearch會找150的還沒expand的新的node。
#### C. UCTSearch()
```python=
    def UCTSearch(self,_rootNode):
        if self.rootNode is None :
            self.rootNode = _rootNode
        
        for i in range(COMPUTE_BUDGET):
            
            expandedNode = self.tree_policy( _rootNode )    # Tree policy

            winner = self.default_policy( expandedNode )    # Default policy

            self.back_up( expandedNode, winner )  # Back up

        return True
```
#### D. Tree_policy()
```python=
    def tree_policy(self, _node):
        # 隨機探索未知的子節點，如果探索完畢就選擇一個最好的子節點
        while _node.get_state().is_not_terminal()  :
            if _node.get_state().is_fully_expanded() is False :
                return self.expand( _node )
            else :
                _node = self.best_child( _node )

        return _node
```
#### E. Best_child()
```python=
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
```
#### F. UCB()
```python=
    def UCB(self,_node,_C=0):
        if _node.get_visitCount() == 0:
            _node.visitCount_add_one()
        left = (float) ( _node.quality_value() )
        right = (float) ( _C*math.sqrt( 2.0*math.log( (float) (_node.parent.get_visitCount())/_node.get_visitCount() ) ) )
        return left+right
```
#### G. Expand()
```python=
    def expand(self,_node):
        # 隨機選擇新的state
        newState = _node.get_state().random_new_state_from_notExpandedAction()

        # 創子節點
        subNode = Node( _state=newState , _parent=_node )
        _node.add_child( subNode )
                
        return subNode
```
#### H. Back_up()
```python=
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
```
#### I. Default_policy()
```python=
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
```
#### J. Load()
```python=
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
```
#### K. Save()
```python=
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
```
