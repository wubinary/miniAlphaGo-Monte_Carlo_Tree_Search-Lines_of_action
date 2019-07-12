var canvas;
var context;
var turn = 'B'; //換誰下 chess:1白色 ，2黑色
var selected = false;
var selected_pt = [0, 0];
var has_winner = false;

var img_b = new Image();
img_b.src = "/static/home/images/b.png"; //黑棋圖片
var img_b_selec = new Image();
img_b_selec.src = "/static/home/images/selecB.png"; //黑棋藍背圖片
var img_b_allow = new Image();
img_b_allow.src = "/static/home/images/allowB.png"; //黑棋橘背圖片
var img_w = new Image();
img_w.src = "/static/home/images/w.png"; //白棋圖片
var img_w_selec = new Image();
img_w_selec.src = "/static/home/images/selecW.png"; //白棋藍背圖片
var img_w_allow = new Image();
img_w_allow.src = "/static/home/images/allowW.png"; //白棋橘背圖片

var img_allow = new Image();
img_allow.src = "/static/home/images/allow.png" //橘色圖片
var img_none = new Image();
img_none.src = "/static/home/images/none.png" //白色圖片

var chessData = new Array(8); //这个为棋盘的二维数组用来保存棋盘信息，初始化0为没有走过的，1为白棋走的，2为黑棋走的
for (var x = 0; x < 8; x++) { //初始化棋盤
    chessData[x] = new Array(8);
    for (var y = 0; y < 8; y++) {
        chessData[x][y] = 0;
    }
}


var is_AI_running=false,makeReq=false,getRep=false;
window.setInterval( function() { if (has_winner==false) AI();}, 500);
function AI() {
    if (has_winner)
        return;

    if (turn=='B' && ai_on_off['B']==1 || turn=='W' && ai_on_off['W']==1){
        if (makeReq==false){
            getMoveRequest();
            makeReq=true;
            return;
        }
        if (getRep==false)
            return;
        console.log(aiMove);

        var x=aiMove['fromX'],y=aiMove['fromY'],dx=aiMove['dirX'],dy=aiMove['dirY'];
        var countChess = countChessOnDir(x, y, dx, dy);

        drawChess(0, x, y); //把from 塗成白色的
        drawChess(turn == 'W' ? 1 : 2, x+dx*countChess, y+dy*countChess); //把to 塗成棋子的顏色

        cleanAllowMoves();

        turn=next_turn();
        document.getElementById('turn').innerHTML=turn=='B'?"turn: BLACK":"turn: WHITE";
    }

    getRep = false;
    makeReq = false;
}

function play(e) { //鼠标点击时发生
    var x = parseInt((e.clientX) / 40);
    var y = parseInt((e.clientY) / 40);

    if (has_winner)
        return;

    if (turn == 'B' && ai_on_off['B'] == 1 || turn == 'W' && ai_on_off['W'] == 1)
        return;

    if (selected == false) {

        selecChess(turn == 'W' ? 1 : 2, x, y);

    } else {

        moveChess(turn == 'W' ? 1 : 2, x, y);

    }

}

var aiMove={'done':0};
function getMoveRequest() { //AI move
    $.ajax({
        type: "POST",
        url: "/request/getmove",
        data: {},
        dataType: "text",
        success: function(dataStr) {
            data = JSON.parse(dataStr);
            aiMove = data;
            getRep = true;

            if (data['has_winner']==1){
                has_winner=true;
                winner=data['winner']=='B'?"BLACK":"WHITE";
                congradulation(winner);
            }

        },
        error: function(error) {
            console.log(error);
        },
        async:true,
    })

}

function makeMoveRequest(context) { //User move
    $.ajax({
        type: "POST",
        url: "/request/makemove",
        data: context,
        dataType: "text",
        success: function(returnStr) {
            console.log(returnStr);
            data = JSON.parse(returnStr);
            if (data['has_winner']==1){
                has_winner=true;
                winner=data['winner']=='B'?"BLACK":"WHITE";
                congradulation(winner);
            }
        },
        error: function(error) {
            console.log(error);
        },
    })
}

function moveChess(chess, x, y) {
    //如果是selected point，取消selected
    if (chessData[x][y] == 3 || chessData[x][y] == 4) {
        cancelSelecChess(x, y);
        selected = false;
        return;
    }

    //判斷此移動是否符合合法移動，並移動棋子
    for (var i = 0; i < allowMoves.length; i++) {
        if (x == allowMoves[i][0] && y == allowMoves[i][1]) {

            var from = [selected_pt[0], selected_pt[1]];
            var to = [x, y];

            drawChess(0, from[0], from[1]); //把from 塗成白色的
            drawChess(turn == 'W' ? 1 : 2, to[0], to[1]); //把to 塗成棋子的顏色

            cleanAllowMoves(); //清掉橘色方格

            makeMoveRequest({
                'type': 'makeMove',
                'turn': turn == 'W' ? 'W' : 'B',
                'fromX': from[0],
                'fromY': from[1],
                'toX': to[0],
                'toY': to[1]
            })

            selected = false;
            turn = next_turn();
            document.getElementById('turn').innerHTML=turn=='B'?"turn: BLACK":"turn: WHITE";
        }
    }
}

function cancelSelecChess(x, y) {

    cleanAllowMoves();

    if (chessData[x][y] == 3)
        drawChess(1, x, y);
    if (chessData[x][y] == 4)
        drawChess(2, x, y);
}

function selecChess(chess, x, y) {
    if (x >= 0 && x < 8 && y >= 0 && y < 8) {
        if (chessData[x][y] == chess) {

            findAllowMoves(chess, x, y);
            if (haveAllowMoves() == false)
                return;
            drawAllowMoves(allowMoves);

            if (chess == 1)
                drawChess(3, x, y);
            else if (chess == 2)
                drawChess(4, x, y);

            selected_pt = [x, y];
            selected = true;
        }
    }
}

function drawAllowMoves() {
    for (var i = 0; i < allowMoves.length; i++)
        drawChess(5, allowMoves[i][0], allowMoves[i][1]);
}

function cleanAllowMoves() {
    for (var i = 0; i < allowMoves.length; i++) {
        if (chessData[allowMoves[i][0]][allowMoves[i][1]] == 0)
            drawChess(0, allowMoves[i][0], allowMoves[i][1]);
        else
            drawChess(chessData[allowMoves[i][0]][allowMoves[i][1]], allowMoves[i][0], allowMoves[i][1]);
    }
    allowMoves = [];
}

/*findAllowMoves*/
var allowMoves = [];

function findAllowMoves(chess, x, y) {

    cleanAllowMoves();

    for (var i = -1; i <= 1; i += 1) {
        for (var j = -1; j <= 1; j += 1) {
            if (i == 0 && j == 0)
                continue;
            
            //計算方向上的棋子數量
            var countChess = countChessOnDir(x, y, i, j), allow=true;

            // 看那點是否還在棋盤中
            if (x + countChess * i < 0 || x + countChess * i >= 8 || y + countChess * j < 0 || y + countChess * j >= 8)
                continue;

            // 看路徑上是否有其他的棋子
            for (var k = 1; k <= countChess - 1; k++)
                if (chessData[x + k * i][y + k * j] != 0 && chessData[x + k * i][y + k * j] != chess)
                    allow=false;

            // 看dst point是否已經有己方旗子
            if (chessData[x + countChess * i][y + countChess * j] == chess)
                continue;

            // 有合法移動
            if (allow)
                allowMoves.push([x + countChess * i, y + countChess * j])
        }
    }
    return allowMoves;
}

function countChessOnDir(x, y, dx, dy) {
    var i = 1,
        count = 1;

    while (x + i * dx >= 0 && x + i * dx < 8 && y + i * dy >= 0 && y + i * dy < 8) { //往(dx,dy) 方向
        if (chessData[x + i * dx][y + i * dy] != 0)
            count += 1;
        i += 1;
    }


    i = -1;
    while (x + i * dx >= 0 && x + i * dx < 8 && y + i * dy >= 0 && y + i * dy < 8) { //往(-dx,-dy) 方向
        if (chessData[x + i * dx][y + i * dy] != 0)
            count += 1;
        i -= 1;
    }
    return count;
}

function haveAllowMoves() {
    return (allowMoves.length > 0)
}
/*findAllowMoves*/

function drawChess(chess, x, y) { //参数为，棋（1为白棋，2为黑棋），数组位置

    if (x >= 0 && x < 8 && y >= 0 && y < 8) {
        if (chess == 0) {
            context.drawImage(img_none, x * 40 + 2, y * 40 + 2); //繪製none
            chessData[x][y] = 0;
        } else if (chess == 1) {
            context.drawImage(img_w, x * 40 + 2, y * 40 + 2); //繪製白棋
            chessData[x][y] = 1;
        } else if (chess == 2) {
            context.drawImage(img_b, x * 40 + 2, y * 40 + 2); //繪製黑棋
            chessData[x][y] = 2;
        } else if (chess == 3) {
            context.drawImage(img_w_selec, x * 40 + 2, y * 40 + 2); //繪製白棋橘底
            chessData[x][y] = 3;
        } else if (chess == 4) {
            context.drawImage(img_b_selec, x * 40 + 2, y * 40 + 2); //繪製黑棋橘底
            chessData[x][y] = 4;
        } else if (chess == 5) {
            if (chessData[x][y] == 1)
                context.drawImage(img_w_allow, x * 40 + 2, y * 40 + 2);
            else if (chessData[x][y] == 2)
                context.drawImage(img_b_allow, x * 40 + 2, y * 40 + 2);
            else
                context.drawImage(img_allow, x * 40 + 2, y * 40 + 2); //繪製橘色底
        }
    }
}


function drawRect() { //页面加载完毕调用函数，初始化棋盘
    canvas = document.getElementById("canvas");
    context = canvas.getContext("2d");

    for (var i = 0; i <= 320; i += 40) { //繪製棋盤的線
        context.beginPath();
        context.moveTo(0, i);
        context.lineTo(320, i);
        context.closePath();
        context.stroke();

        context.beginPath();
        context.moveTo(i, 0);
        context.lineTo(i, 320);
        context.closePath();
        context.stroke();
    }


    for (var i = 1; i < 7; i++) { //繪製黑棋白棋
        drawChess(2, i, 0);
        drawChess(2, i, 7);
        drawChess(1, 0, i);
        drawChess(1, 7, i);
    }
}

var ai_on_off = { 'B': 0, 'W': 0 }; //[B,W]
function AI_on_off(who) {
    if (who == 'B') {
        ai_on_off['B'] = ai_on_off['B']==1 ? 0 : 1;
        document.getElementById("ai_on_off_B").innerHTML = ai_on_off['B']==1 ? "ON" : "OFF";
    }
    if (who == 'W') {
        ai_on_off['W'] = ai_on_off['W']==1 ? 0 : 1;
        document.getElementById("ai_on_off_W").innerHTML = ai_on_off['W']==1 ? "ON" : "OFF";
    }
    startTime = new Date().getTime();
}

function next_turn(){
    if (turn=='B') 
        turn='W';
    else
        turn='B';
    startTime = new Date().getTime();
    return turn;
}

function congradulation(winner){
    document.getElementById("turn").innerHTML = "Congradulation Winner : " + winner;
    alert("已經結束了\nwinner: "+winner+"\n如果需要重玩，請刷新");
    window.location.href=window.location.href;
}


var startTime = new Date().getTime();
var downCounter = setInterval(function() {

  // Get today's date and time
  var now = new Date().getTime();
    
  // Find the distance between now and the count down date
  var distance = 61000 - (now - startTime);
    
  // Time calculations for days, hours, minutes and seconds
  var minutes = Math.floor((distance % (1000 * 60 * 60)) / (1000 * 60));
  var seconds = Math.floor((distance % (1000 * 60)) / 1000);
    
  // Output the result in an element with id="demo"
  document.getElementById("downCounter").innerHTML = minutes + "m " + seconds + "s ";
    
  // If the count down is over, write some text 
  if (distance < 0) {
    clearInterval(x);
    document.getElementById("downCounter").innerHTML = "EXPIRED";
  }
}, 100);