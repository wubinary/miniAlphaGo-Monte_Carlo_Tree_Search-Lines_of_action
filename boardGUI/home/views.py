from django.shortcuts import render

# Create your views here.
from django.http import HttpResponseRedirect,JsonResponse
from django.urls import reverse

#加入prent dir
import sys
sys.path.append("..")

from mcts import *


mcts = Monte_Carlo_Tree_Search()
selecModel = -1
while selecModel!=2 and selecModel!=1 :
    selecModel = input("\tTwo pre train models:\n\n"+
                       "\t [1]  light weight model ，3MB\n\t      loading need <1SEC \n"+
                       "\t [2]  full model ，3GB\n\t      free ram space >=3G，loading need 10MIN\n\n"+
                       "\t  load light model:1\n\t  load full model:2\n\t\tmy selection:")
    selecModel = int(selecModel)
print("\n\t[Info] loading mcts model......, please wait !!!")
if selecModel==1:
    mcts.load(_path="/model_sm/")
else:
    mcts.load()
print("\n\t[Info] load mcts model complete!!")

nodePtDict = {}

def home(request):
    return render(request,'home/home.html')

def div(n, d):
    return n / d if d else 0
def makemove(request): #User move
    # 產生nodePt
    make_node_pt(request.POST['csrfmiddlewaretoken'])
    nodePt = nodePtDict[request.POST['csrfmiddlewaretoken']]

    req = dict(request.POST.copy())
    del req['csrfmiddlewaretoken']
    _role = role["WHITE"] if req['turn'][0]=="W" else role["BLACK"]
    _point = [int(req['fromY'][0]),int(req['fromX'][0])]
    _direct = [int(div(int(req['toY'][0])-int(req['fromY'][0]),abs(int(req['toY'][0])-int(req['fromY'][0])))),
               int(div(int(req['toX'][0])-int(req['fromX'][0]),abs(int(req['toX'][0])-int(req['fromX'][0]))))]

    # 用action 尋找childNode
    action = {"role":_role, "point":_point, "direction":_direct}  #{"role":_role,"point":[pt.y,pt.x],"direction":list(direction)}
    childNode = nodePt.get_childNode_by_action( action )
    nodePtDict[request.POST['csrfmiddlewaretoken']] = childNode

    # 後台棋盤graph
    boardTmp=Board(_board=childNode.get_state().get_board())
    boardTmp.graph()
    final,winner = boardTmp.has_winner()

    if final is True:
        return JsonResponse({'status':'success','has_winner':1,'winner': 'W' if winner==role["WHITE"] else 'B' ,'request':req})
    return JsonResponse({'status':'success','has_winner':0,'request':req})

def getmove(request): #AI move
    # 產生nodePt
    make_node_pt(request.POST['csrfmiddlewaretoken'])
    nodePt = nodePtDict[request.POST['csrfmiddlewaretoken']]

    req = dict(request.POST.copy())
    del req['csrfmiddlewaretoken']

    mcts.UCTSearch( _rootNode=nodePt )
    bestChild = mcts.best_child(nodePt,is_exploration=False)
    nodePtDict[request.POST['csrfmiddlewaretoken']] = bestChild

    action = bestChild.get_state().get_action()
    move = {'turn': "B" if action["role"]==role["BLACK"] else "W",
            'fromX':action["point"][1],'fromY':action["point"][0],'dirX':action["direction"][1],'dirY':action["direction"][0]}

    # 後台棋盤graph
    boardTmp=Board(_board=bestChild.get_state().get_board())
    boardTmp.graph()
    final,winner = boardTmp.has_winner()

    if final is True:
        move.update({'status':'success','done':0,'has_winner':1,'winner': 'W' if winner==role["WHITE"] else 'B'})
    move.update({'status':'success','done':0,'has_winner':0})
    return JsonResponse(move)
    
def jason(request):
    return JsonResponse({'foo':'bar'})

def make_node_pt(csrftoken):
    if csrftoken in [tk for tk in nodePtDict.keys()]:
        return
    nodePtDict[csrftoken] = mcts.rootNode #mcts.rootNode
    
